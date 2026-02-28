import bpy
import gmsh
import bmesh
import json
import math
from mathutils import Vector

SIMULATION_FRAMES = 30
SIMULATION_QUALITY = 30
CLOTH_SETTINGS = {
    "mass": 0.5,
    "tension_stiffness": 15,
    "compression_stiffness": 15,
    "shear_stiffness": 15,
    "bending_stiffness": 1.0,
    "tension_damping": 5,
    "compression_damping": 5,
    "shear_damping": 5,
    "bending_damping": 5,
    "sewing_force_max": 100,
    "use_self_collision": True,
    "self_friction": 5.0,
    "fixed_vertices": "fixed_vertices",
    "self_distance_min": 0.02,
    "use_collision": True,
    "friction": 0.0,
}

GRAVITY = (0, 0, -9.81)


"""
========[シミュレーション設定]========
"""


def apply_cloth_modifier(obj):
    # オブジェクトを選択してアクティブに設定
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # オブジェクトモードに設定
    bpy.ops.object.mode_set(mode="OBJECT")

    # Cloth Modifierを適用
    bpy.ops.object.modifier_add(type="CLOTH")
    cloth_settings = bpy.context.object.modifiers["Cloth"].settings

    # シミュレーション品質を向上
    cloth_settings.quality = SIMULATION_QUALITY

    # 縫製設定
    cloth_settings.use_sewing_springs = True
    cloth_settings.sewing_force_max = CLOTH_SETTINGS["sewing_force_max"]
    cloth_settings.vertex_group_mass = CLOTH_SETTINGS["fixed_vertices"]

    # 質量設定
    cloth_settings.mass = CLOTH_SETTINGS["mass"]

    # 剛性設定（より現実的な布の動き）
    cloth_settings.tension_stiffness = CLOTH_SETTINGS["tension_stiffness"]
    cloth_settings.compression_stiffness = CLOTH_SETTINGS["compression_stiffness"]
    cloth_settings.shear_stiffness = CLOTH_SETTINGS["shear_stiffness"]
    cloth_settings.bending_stiffness = CLOTH_SETTINGS["bending_stiffness"]

    # ダンピング設定
    cloth_settings.tension_damping = CLOTH_SETTINGS["tension_damping"]
    cloth_settings.compression_damping = CLOTH_SETTINGS["compression_damping"]
    cloth_settings.shear_damping = CLOTH_SETTINGS["shear_damping"]
    cloth_settings.bending_damping = CLOTH_SETTINGS["bending_damping"]

    # 自己衝突の設定
    collision_settings = bpy.context.object.modifiers["Cloth"].collision_settings
    collision_settings.use_self_collision = CLOTH_SETTINGS["use_self_collision"]
    collision_settings.self_distance_min = CLOTH_SETTINGS["self_distance_min"]
    collision_settings.self_friction = CLOTH_SETTINGS["self_friction"]

    # 外部衝突の設定
    collision_settings.use_collision = CLOTH_SETTINGS["use_collision"]
    collision_settings.friction = CLOTH_SETTINGS["friction"]

    # スムースシェーディングを適用
    bpy.ops.object.shade_smooth()

    # オブジェクトの選択を解除
    obj.select_set(False)


def flip_normal(ref_obj, obj_to_modify):
    """
    align the normal of the given object to the positive y-axis if the face is above the threshold, otherwise align to negative y-axis
    """
    # threshold_vec =calculate_centroid(ref_obj)
    threshold_y = ref_obj.location.y
    # threshold_vec.y
    print(f"しきい値のY座標: {threshold_y}")

    positive_y_normal = Vector((0, 1, 0))
    negative_y_normal = Vector((0, -1, 0))

    bpy.context.view_layer.objects.active = obj_to_modify
    # --- 設定ここまで ---

    # オブジェクトがメッシュであることを確認
    if obj_to_modify and obj_to_modify.type == "MESH":
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj_to_modify.data)

        world_matrix = obj_to_modify.matrix_world

        for face in bm.faces:
            local_center = face.calc_center_median()
            world_center = world_matrix @ local_center
            if world_center.y < threshold_y:
                target_normal = negative_y_normal
            else:
                target_normal = positive_y_normal

            world_normal = (world_matrix.to_3x3() @ face.normal).normalized()
            dot_product = world_normal.dot(target_normal)

            if dot_product < 0:
                face.normal_flip()

        bm.normal_update()

        bmesh.update_edit_mesh(obj_to_modify.data)

        bpy.ops.object.mode_set(mode="OBJECT")

        print("処理完了")

    else:
        print("処理対象がメッシュオブジェクトではありません")


def add_collision_modifier(obj):
    """指定されたオブジェクトに衝突設定を追加する関数"""
    if obj is None:
        raise ValueError("No object provided")

    # オブジェクトを選択してアクティブに設定
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Collision Modifierを追加
    bpy.ops.object.modifier_add(type="COLLISION")

    # オブジェクトの選択を解除
    obj.select_set(False)


def update_simulation(obj, frames):
    """
    改善されたシミュレーション実行関数
    """
    print("シミュレーションを開始します...")

    # オブジェクトモードに設定
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    bpy.ops.object.shade_smooth()

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # シミュレーション設定
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    # 物理シミュレーションの設定
    bpy.context.scene.use_gravity = True
    bpy.context.scene.gravity = GRAVITY  # 重力を設定

    # シミュレーションの実行
    print(f"フレーム 1 から {frames} までシミュレーションを実行中...")

    for frame_no in range(1, frames + 1):
        if frame_no % 1 == 0:  # 50フレームごとにプログレス表示
            print(
                f"フレーム {frame_no}/{frames} を実行中... ({frame_no/frames*100:.1f}%)"
            )

        bpy.context.scene.frame_set(frame_no)

        # キーフレームを挿入（重要なフレームのみ）
        if frame_no % 10 == 0 or frame_no == frames:
            obj.keyframe_insert(data_path="location")
            obj.keyframe_insert(data_path="rotation_euler")

    print("シミュレーションが完了しました！")
    bpy.ops.object.shade_smooth()


def export_glb(filepath):
    """Export the current Blender scene to a GLB file."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        use_visible=True,
        export_animations=True,
        export_yup=True,
        export_apply=True,
    )

    try:
        print(f"Successfully exported GLB file: {filepath}")
    except Exception as e:
        print(f"Failed to export GLB file: {filepath}. Error: {e}")
