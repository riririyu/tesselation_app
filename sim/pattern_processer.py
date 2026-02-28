import bpy
import gmsh
import bmesh
import json
import math
from mathutils import Vector
import config


def subdivide_curve(curve_obj):
    num_stitch = config.SEWING_SETTINGS["num_stitch"]
    bpy.context.view_layer.objects.active = curve_obj

    mod = curve_obj.modifiers.get("GeometryNodes")
    if not mod:
        mod = curve_obj.modifiers.new(name="GeometryNodes", type="NODES")
    mod.node_group = build_resample_node_tree(num_stitch)
    print(f"Applied Geometry Nodes modifier to {curve_obj.name} for resampling.")


def build_resample_node_tree(num_stitch):
    """
    ジオメトリノードグループを作成し、カーブを一定間隔でリサンプリングするノードツリーを構築する
    """
    group_name = "Resample"
    node_group = bpy.data.node_groups.new(group_name, "GeometryNodeTree")

    node_group.interface.new_socket(
        name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    node_group.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    nodes = node_group.nodes
    links = node_group.links

    in_node = nodes.new("NodeGroupInput")
    out_node = nodes.new("NodeGroupOutput")
    resample = nodes.new("GeometryNodeResampleCurve")
    resample.mode = "COUNT"
    resample.inputs[2].default_value = num_stitch

    c2m = nodes.new("GeometryNodeCurveToMesh")

    links.new(in_node.outputs[0], resample.inputs[0])
    links.new(resample.outputs[0], c2m.inputs[0])
    links.new(c2m.outputs[0], out_node.inputs[0])

    return node_group


# ---fill the faces---
def convert_to_mesh(obj):
    """Fill faces for all mesh objects in the scene."""
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    print(f"Converted curve to mesh: {obj.name}")
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    if False:

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.fill()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        print(f"Filled faces for mesh: {obj.name}")


# 面を生成
def create_faces(mesh_obj):
    # オブジェクトを選択してアクティブに設定
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # オブジェクトモードに切り替え（念のため）
    bpy.ops.object.mode_set(mode="OBJECT")

    # 編集モードに切り替え
    bpy.ops.object.mode_set(mode="EDIT")

    # 編集モードかどうか確認
    if bpy.context.mode != "EDIT_MESH":
        print(
            f"警告: 編集モードに切り替えできませんでした。現在のモード: {bpy.context.mode}"
        )
        return

    bm = bmesh.from_edit_mesh(mesh_obj.data)

    # すべての頂点を選択
    bpy.ops.mesh.select_all(action="SELECT")

    # 面を作成
    try:
        bmesh.ops.contextual_create(bm, geom=bm.edges, mat_nr=0, use_smooth=False)
    except Exception as e:
        print(f"面の作成中にエラーが発生しました: {e}")
        # エッジから面を作成する代替方法を試す
        try:
            bpy.ops.mesh.edge_face_add()
        except Exception as e2:
            print(f"代替方法でも面の作成に失敗しました: {e2}")

    # bmesh を更新
    bmesh.update_edit_mesh(mesh_obj.data)

    # オブジェクトモードに戻す
    bpy.ops.object.mode_set(mode="OBJECT")

    return mesh_obj


# -------リメッシュ-------
def remesh_by_gmsh(target_obj, lc):
    bm = bmesh.new()
    bm.from_mesh(target_obj.data)

    boundary_edges = [e for e in bm.edges if e.is_boundary]
    if not boundary_edges:
        print("Error: No boundary edges found. Make sure it's a flat polygon.")
        return

    # 頂点を順序通りに並べる
    ordered_coords = []
    start_vert = boundary_edges[0].verts[0]
    curr_vert = start_vert

    visited_edges = set()
    for _ in range(len(boundary_edges)):
        for edge in curr_vert.link_edges:
            if edge.is_boundary and edge not in visited_edges:
                visited_edges.add(edge)
                curr_vert = edge.other_vert(curr_vert)
                ordered_coords.append(curr_vert.co.copy())
                break

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("Blender_Remesh")
    # generate bese shapes
    p_tags = [gmsh.model.geo.addPoint(p.x, p.y, p.z, lc) for p in ordered_coords]
    l_tags = [
        gmsh.model.geo.addLine(p_tags[i], p_tags[(i + 1) % len(p_tags)])
        for i in range(len(p_tags))
    ]
    cl = gmsh.model.geo.addCurveLoop(l_tags)
    surface = gmsh.model.geo.addPlaneSurface([cl])
    # remesh
    gmsh.model.geo.synchronize()
    gmsh.option.setNumber("Mesh.Algorithm", 8)

    gmsh.model.mesh.generate(2)

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    nodes = coords.reshape(-1, 3)
    elem_types, elem_tags, node_indices = gmsh.model.mesh.getElements(2)

    faces = []
    for i, e_type in enumerate(elem_types):
        nodes_per_elem = 3 if e_type == 2 else 4
        v_list = node_indices[i]
        for j in range(0, len(v_list), nodes_per_elem):
            faces.append([int(idx) - 1 for idx in v_list[j : j + nodes_per_elem]])

    gmsh.finalize()
    mesh = target_obj.data
    mesh.clear_geometry()
    mesh.from_pydata(nodes, [], faces)
    mesh.update()
    bm.free()


def create_vertex_groups_for_edges(obj, split_points, split_points_names):
    """
    指定されたオブジェクトに対して、エッジの座標をもとに頂点グループを作成します。
    """
    num_stitch = config.SEWING_SETTINGS["num_stitch"]
    edge_points = []
    edge_points = split_points.copy()
    edge_points.append(split_points[0])
    names = split_points_names.copy()
    names.append(split_points_names[0])

    for idx, (start_coord, end_coord, start_name, end_name) in enumerate(
        zip(
            edge_points[:-1],
            edge_points[1:],
            names[:-1],
            names[1:],
        )
    ):
        print(f"Processing edge {idx}: start {start_coord}, end {end_coord}")
        edge_name = f"{obj.name}_{start_name}_{end_name}"

        start_3d_coord = Vector((start_coord[0], start_coord[1], 0))
        end_3d_coord = Vector((end_coord[0], end_coord[1], 0))

        start_vertex_index = find_closest_vertex_index(obj, start_3d_coord)
        end_vertex_index = find_closest_vertex_index(obj, end_3d_coord)

        # print(f"開始点のインデックス: {start_vertex_index}")
        # print(f"終了点のインデックス: {end_vertex_index}")

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        # インデックスが有効か（subdivide 後の崩れ対策）
        if (
            start_vertex_index < 0
            or start_vertex_index >= len(bm.verts)
            or end_vertex_index < 0
            or end_vertex_index >= len(bm.verts)
        ):
            print(
                f"[WARN] invalid indices after topology change: s={start_vertex_index}, e={end_vertex_index}"
            )
            bpy.ops.object.mode_set(mode="OBJECT")
            # フォールバック：端点だけのグループ
            add_vertices_to_group(
                obj,
                [max(0, start_vertex_index), max(0, end_vertex_index)],
                edge_name,
            )
            continue

        bpy.ops.mesh.select_all(action="DESELECT")
        bm.verts[start_vertex_index].select = True
        bm.verts[end_vertex_index].select = True
        # ビューポートへ反映
        bmesh.update_edit_mesh(obj.data)

        # 選択モードを頂点に固定（オペレータ安定化）
        try:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
        except Exception as e:
            print(f"[INFO] select_mode set failed (VERT): {e}")

        # --- 最短パス選択 ---
        try:
            bpy.ops.mesh.shortest_path_select(edge_mode="SELECT")
        except Exception as e:
            print(f"[WARN] shortest_path_select failed: {e}")

        # ここでテーブル再構築（shortest_path_select で内部状態が変わることがある）
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        # 選択した頂点のIndexを取得
        vertices_on_shortest_path = [v.index for v in bm.verts if v.select]
        sorted_verts = []
        current_v = bm.verts[start_vertex_index]

        while current_v.index != end_vertex_index:
            # print(f"current_v:{current_v.index} loop start")
            next_v = None
            for edge in current_v.link_edges:
                v_other = edge.other_vert(current_v)
                # print(f"linked vert: {v_other.index}{v_other.co}")
                if v_other.index in vertices_on_shortest_path:
                    if (
                        v_other.index not in sorted_verts
                        and v_other.index != start_vertex_index
                    ):
                        next_v = v_other
                        break
            if next_v is None:
                print(
                    f"[WARN] could not find next vertex from {current_v.index}; breaking"
                )
                break  # ループを抜ける

            sorted_verts.append(next_v.index)
            current_v = next_v

        if len(sorted_verts) < 2 * num_stitch:
            vertex_indices = sorted_verts

        else:
            distance = []
            total = 0.0
            previous_coord = bm.verts[start_vertex_index].co
            for v_idx in sorted_verts:
                v = bm.verts[v_idx]
                total += (v.co - previous_coord).length
                distance.append(total)
                previous_coord = v.co
            # print(f"distance: {distance}")

            vertex_indices = []
            for j in range(num_stitch):
                target_dist = total * (j + 1) / (num_stitch + 1)
                # print(f"target dist: {target_dist}")
                error = 100
                for i, dist in enumerate(distance):
                    if abs(dist - target_dist) < error:
                        error = abs(dist - target_dist)
                        closest_v = i
                vertex_indices.append(sorted_verts[closest_v])

        # ここでテーブル再構築（shortest_path_select で内部状態が変わることがある）
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        # オブジェクトモードに戻す前に bmesh を反映
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

        vertex_indices.insert(0, start_vertex_index)
        vertex_indices.append(end_vertex_index)
        # print(f"vertex_indices: {vertex_indices}")
        add_vertices_to_group(obj, vertex_indices, edge_name)


# ----参照関数-----
def find_closest_vertex_index(obj, coord):
    mesh = obj.data
    closest_index = -1
    min_distance = float("inf")
    for i, vertex in enumerate(mesh.vertices):
        world_vertex = obj.matrix_world @ vertex.co
        distance = (world_vertex - coord).length
        if distance < min_distance:
            min_distance = distance
            closest_index = i
    return closest_index


def sort_by_vertex_distances(obj, selected_indices, start_vertex_index):
    """
    EDITモード不要の安全版。
    メッシュのローカル座標を matrix_world でワールドに変換して距離ソート。
    """
    mesh = obj.data
    if start_vertex_index < 0 or start_vertex_index >= len(mesh.vertices):
        return selected_indices  # そのまま返すフォールバック

    start_local = mesh.vertices[start_vertex_index].co
    start_world = obj.matrix_world @ start_local

    vertex_distances = []
    for vidx in selected_indices:
        if 0 <= vidx < len(mesh.vertices):
            v_local = mesh.vertices[vidx].co
            v_world = obj.matrix_world @ v_local
            d = (v_world - start_world).length
            vertex_distances.append((vidx, d))

    vertex_distances.sort(key=lambda x: x[1])
    return [idx for idx, _ in vertex_distances]


def add_vertices_to_group(obj, vertex_indices, group_name):
    group = obj.vertex_groups.get(group_name)
    if not group:
        group = obj.vertex_groups.new(name=group_name)

    # 空配列なら何もしない（安全側）
    if not vertex_indices:
        print(f"[WARN] {group_name}: empty vertex_indices; skip")
        return

    # 重複除去（順序維持）
    seen = set()
    deduped = []
    for vid in vertex_indices:
        if vid not in seen:
            seen.add(vid)
            deduped.append(vid)
    vertex_indices = deduped

    n = len(vertex_indices)

    # print(f"[INFO] {group_name}: added {n} vertices to group")
    if n == 1:
        # 1点だけなら 1.0 で追加（0除算回避）
        group.add([vertex_indices[0]], 1.0, "ADD")
        return

    # 2点以上：0→1 に正規化してウェイト付与
    denom = float(n - 1)
    for i, v_idx in enumerate(vertex_indices):
        w = i / denom
        # 念のためクランプ
        if w < 0.0:
            w = 0.0
        if w > 1.0:
            w = 1.0
        group.add([v_idx], w, "ADD")


def duplicate_and_mirror_objects(obj):
    print(f"Duplicating and mirroring object: {obj.name}")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)

    bpy.ops.object.duplicate()

    mirrored_obj = bpy.context.selected_objects[0]
    mirrored_obj.name = obj.name + "_left"
    mirrored_obj.scale[0] *= -1
    bpy.ops.object.transform_apply(scale=True)

    for group in mirrored_obj.vertex_groups:
        group.name = group.name.replace(obj.name, obj.name + "_left")

    return mirrored_obj


def bend_waistbelt(panel_name):
    curve_obj = create_ellipse(r_x=0.2, r_y=0.15)

    obj = bpy.data.objects.get(panel_name)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(name="MyCurveMod", type="CURVE")
    mod.object = curve_obj
    mod.deform_axis = "POS_X"
    curve_obj.data.use_stretch = False
    curve_obj.data.use_deform_bounds = False
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(curve_obj, do_unlink=True)


def create_ellipse(r_x, r_y) -> bpy.types.Object:
    bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object

    obj.scale[0] = r_x
    obj.scale[1] = r_y
    obj.scale[2] = 1.0
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def locate_panel_obj_on_body(joint_data):
    """Locate panel objects on the body model based on keypoints."""
    # locate fr
    obj = bpy.data.objects.get("front_bodice_d")
    obj.location = (
        joint_data["right_knee"][0],
        2 * joint_data["right_big_toe"][2],
        joint_data["right_knee"][1],
    )

    obj = bpy.data.objects.get("front_bodice_d_left")
    obj.location = (
        joint_data["left_knee"][0],
        1.5 * joint_data["left_big_toe"][2],
        joint_data["left_knee"][1],
    )

    obj = bpy.data.objects.get("back_bodice")
    obj.location = (
        joint_data["right_knee"][0],
        -2 * joint_data["right_big_toe"][2],
        joint_data["right_knee"][1],
    )

    obj = bpy.data.objects.get("back_bodice_left")
    obj.location = (
        joint_data["left_knee"][0],
        -1.5 * joint_data["left_big_toe"][2],
        joint_data["left_knee"][1],
    )

    obj = bpy.data.objects.get("yoke")
    obj.rotation_euler[1] = math.radians(-90)
    obj.location = (
        joint_data["right_knee"][0],
        -1.5 * joint_data["right_big_toe"][2],
        joint_data["spine1"][1],
    )
    obj = bpy.data.objects.get("yoke_left")
    obj.rotation_euler[1] = math.radians(90)
    obj.location = (
        joint_data["left_knee"][0],
        -1.5 * joint_data["left_big_toe"][2],
        joint_data["spine1"][1],
    )

    obj = bpy.data.objects.get("waist_belt")

    obj.location = (
        joint_data["left_knee"][0],
        -1.5 * joint_data["left_big_toe"][2],
        joint_data["spine1"][1],
    )


def set_fixed_vertices(obj, group_name):
    vertices = []
    add_vertices_to_group(obj, vertices, group_name)


def join_all_mesh_objects(obj_list):

    if not obj_list:
        print("警告: 結合するメッシュオブジェクトが見つかりません")
        return None

    # 全てのオブジェクトの選択を解除
    try:
        bpy.ops.object.select_all(action="DESELECT")
    except Exception as e:
        print(f"オブジェクト選択解除エラー: {e}")
        # 手動で選択を解除
        for obj in bpy.context.scene.objects:
            obj.select_set(False)

    # メッシュオブジェクトを選択
    for obj in obj_list:
        obj.select_set(True)

    # 最初のオブジェクトをアクティブに設定
    if obj_list:
        bpy.context.view_layer.objects.active = obj_list[0]

    # 選択されたオブジェクトを結合
    try:
        bpy.ops.object.join()
        joined_obj = bpy.context.view_layer.objects.active
        joined_obj.name = "joined_pattern"

        return joined_obj

    except Exception as e:
        print(f"オブジェクト結合エラー: {e}")
        # 結合に失敗した場合は最初のオブジェクトを返す
        return obj_list[0] if obj_list else None


def create_edges_between_groups(joined_obj, edge_data):
    """二つの頂点グループ間に縫製エッジを追加する関数"""

    # mesh_obj, group1, group2, group1_percent, group2_percent
    for data in edge_data["combination"]:
        panael1 = data["panel"][0]
        panael2 = data["panel"][1]
        for edge in data["sewing_edges"]:
            point_a = edge[0]
            point_b = edge[1]
            group1 = search_existing_group_name(joined_obj, panael1, point_a, point_b)
            group2 = search_existing_group_name(joined_obj, panael2, point_a, point_b)

            # ウェイト順に並べ替え
            vertices_group1 = select_vertices_sorted_by_weight(joined_obj, group1, 1.0)
            vertices_group2 = select_vertices_sorted_by_weight(joined_obj, group2, 1.0)

            # 編集モードに切り替え
            bpy.context.view_layer.objects.active = joined_obj
            bpy.ops.object.mode_set(mode="EDIT")

            # bmeshを使用してメッシュデータを取得
            bm = bmesh.from_edit_mesh(joined_obj.data)
            bm.verts.ensure_lookup_table()

            # どちらのリストが短いかを判断する
            if len(vertices_group1) < len(vertices_group2):
                # vertices_group1が短い場合、それを逆順にする
                shorter_list = vertices_group1
                longer_list = vertices_group2
            else:
                # vertices_group2が短い場合、それを逆順にする
                shorter_list = vertices_group2
                longer_list = vertices_group1

            # 辺を追加
            for v1, v2 in zip(shorter_list, longer_list):
                if v1 != v2:
                    if bm.edges.get((bm.verts[v1], bm.verts[v2])) is None:
                        bm.edges.new((bm.verts[v1], bm.verts[v2]))

            # bmeshを更新
            bmesh.update_edit_mesh(joined_obj.data)

            # オブジェクトモードに戻る
            bpy.ops.object.mode_set(mode="OBJECT")


# --参照関数--
def search_existing_group_name(joined_obj, panel_name, point_a, point_b):
    name_option = f"{panel_name}_{point_a}_{point_b}"
    if name_option in joined_obj.vertex_groups:
        return name_option
    else:
        return f"{panel_name}_{point_b}_{point_a}"


def select_vertices_sorted_by_weight(mesh_obj, group_name, percent):
    """特定の頂点グループ(group_name)からウェイト順に頂点を取得する関数"""
    print(f"Selecting vertices from  '{mesh_obj.name}'")
    group_index = mesh_obj.vertex_groups[group_name].index
    weight_vertex_pairs = []

    for v in mesh_obj.data.vertices:
        for g in v.groups:
            if g.group == group_index:
                weight_vertex_pairs.append((g.weight, v.index))
                break

    # ウェイトに基づいてソート
    weight_vertex_pairs.sort(key=lambda x: x[0], reverse=True)

    # 指定された割合に基づいて頂点を選択
    if percent < 0:
        percent = -percent
        selected_vertices = weight_vertex_pairs[
            int(len(weight_vertex_pairs) * (1 - percent)) :
        ]
    else:
        selected_vertices = weight_vertex_pairs[
            : int(len(weight_vertex_pairs) * percent)
        ]

    return [pair[1] for pair in selected_vertices]


def redefine_curve(
    obj, start_name, end_name, distance, split_points, split_points_names
):
    num_stitch = config.SEWING_SETTINGS["num_stitch"]

    # get coordinates of start and end points
    start_index = split_points_names.index(start_name)
    end_index = split_points_names.index(end_name)
    start_coord = split_points[start_index]
    end_coord = split_points[end_index]

    group_name = search_existing_group_name(obj, start_name, end_name)

    # convert to polyline curve
    # split curve
    # subdivide curve in stitch points
    # create new vertex group
