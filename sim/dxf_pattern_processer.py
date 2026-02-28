import bpy
import gmsh
import bmesh
import json
import math
from mathutils import Vector


def visualize_split_points(key_points, radius):
    for part_key, item in key_points["parts"].items():
        for property in item["keypoints"]:
            x = property["x"]
            y = property["y"]
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(x, y, 0))
            obj = bpy.context.object
            obj.name = f"{property['label']}"


def import_patterns(dxf_filepaths, keypoints_filepath, object_names):
    """generate object from dxf files"""
    for filepath in dxf_filepaths:
        objects_before = set(bpy.data.objects.keys())
        import_dxf(str(filepath))
        # Two objects are created per DXF file
        objects_after = set(bpy.data.objects.keys())
        new_objects = objects_after - objects_before
        print(f"{objects_before} -> {objects_after}")
        if new_objects:
            for obj_name in new_objects:
                obj = bpy.data.objects[obj_name]
                print(f"Imported pattern: {obj.name}")
                # Rename object which is liked to the scene
                if obj.name in bpy.context.scene.objects:
                    new_name = object_names.get(extract_name_from_filepath(filepath))
                    obj.name = new_name
                    print(f"renamed to {new_name}")
                if obj.data.users > 1:
                    obj.data = obj.data.copy()

                bpy.context.view_layer.update()


def import_dxf(filepath):
    """Import a DXF file into Blender."""
    try:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.import_scene.dxf(filepath=filepath)
        # print(f"Successfully imported DXF file: {filepath}")
    except Exception as e:
        print(f"Failed to import DXF file: {filepath}. Error: {e}")


def extract_name_from_filepath(filepath):
    """Extract the file name without extension from a file path."""
    filename = str(filepath).split("/")[-1]
    part_name = filename.split(".dxf")[0]
    short_name = part_name.split(".")[-1]
    return short_name


def split_curve(obj, split_points):
    print(f"Splitting curve: {obj.name}")
    bpy.ops.object.mode_set(mode="EDIT")
    spline = obj.data.splines[0]
    spline.use_cyclic_u = True
    for idx, (start_coord, end_coord) in enumerate(
        zip(split_points[:-1], split_points[1:])
    ):
        bpy.context.view_layer.update()

        start_3d_coord = Vector((start_coord[0], start_coord[1], 0))
        end_3d_coord = Vector((end_coord[0], end_coord[1], 0))

        start_point_index = -1
        end_point_index = -1
        spline_index = -1

        for i in range(len(obj.data.splines)):
            bpy.context.view_layer.update()
            start_point_index = find_closest_points_index(obj, i, start_3d_coord)
            if start_point_index != -1:
                end_point_index = find_closest_points_index(obj, i, end_3d_coord)
                if start_point_index != -1 and end_point_index != -1:
                    spline_index = i
                    break

        if spline_index != -1:
            spline = obj.data.splines[spline_index]
        else:
            raise ValueError(
                f"Could not find a spline containing both points for edge {idx} in {obj.name}"
            )

        # print(f"開始点のインデックス: {start_point_index}")
        # print(f"終了点のインデックス: {end_point_index}")
        for p in spline.points:
            p.select = False
        smaller_index = min(start_point_index, end_point_index)
        larger_index = max(start_point_index, end_point_index)
        for i in range(smaller_index, larger_index + 1):
            spline.points[i].select = True
        bpy.ops.curve.split()

    bpy.ops.object.mode_set(mode="OBJECT")


"""---分割点の座標とを抽出---"""


def extract_split_points_names_from_keypoints(obj, keypoints_data):
    data = keypoints_data["parts"][obj.name]["keypoints"]
    split_points_names = []
    for property in data:
        split_points_names.append(property["label"])
    print(f"split_points_names: {split_points_names}")
    return split_points_names


def extract_split_points_from_keypoints(keypoints_data, panel_name):
    data = keypoints_data["parts"][panel_name]["keypoints"]
    split_points = []
    for property in data:
        split_points.append((property["x"], property["y"]))
    print(f"split_points: {split_points}")
    return split_points


""" ALTERNATIVE function"""


def extract_split_points_from_index(obj, keypoints_data):
    split_points = []

    split_indices = extract_split_index_from_keypoints(keypoints_data, obj.name)
    # split_points = extract_split_points_from_keypoints(keypoints_data, obj.name)

    bpy.context.view_layer.objects.active = obj
    for idx in split_indices:
        bpy.context.view_layer.update()
        spline = obj.data.splines[0]
        point = spline.points[idx]
        local_coord = point.co.xyz
        split_points_coord = obj.matrix_world @ local_coord
        split_points.append((split_points_coord.x, split_points_coord.y))
    return split_points


def extract_split_index_from_keypoints(keypoints_data, panel_name):
    data = keypoints_data["parts"][panel_name]["keypoints"]
    split_indices = []
    for property in data:
        split_indices.append(property["vertex_index"])
    print(split_indices)
    return split_indices


def find_closest_points_index(obj, spline_idx, coord):
    spline = obj.data.splines[spline_idx]
    points = spline.points
    closest_index = -1
    min_distance = float("inf")
    for i, vertex in enumerate(points):
        world_vertex = obj.matrix_world @ vertex.co.xyz
        distance = (world_vertex - coord).length
        if distance < min_distance:
            min_distance = distance
            closest_index = i

    # print(f"Minimum distance for spline {spline_idx}-{closest_index}: {min_distance}")
    if min_distance < 0.5:  # 適切な閾値を設定
        return closest_index
    else:
        return -1
