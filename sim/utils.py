import bpy
import gmsh
import bmesh
import json
import math
from mathutils import Vector


def purge_all_curves_and_meshes():
    """
    シーン内の全てのカーブとメッシュの「オブジェクト」と「データ」を完全に削除する
    """
    if not bpy.data.objects:
        return
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)

    print(f"オブジェクトを削除しました。")


def import_obj(filepath, scale: float = 1.0) -> bpy.types.Object:
    filepath_str = str(filepath)
    bpy.ops.wm.obj_import(
        filepath=filepath_str,
        forward_axis="NEGATIVE_Z",
        up_axis="Y",
    )

    obj = bpy.context.selected_objects[0]
    obj.rotation_euler = (math.radians(90), 0, math.radians(180))
    bpy.context.view_layer.update()

    obj.scale = (scale, scale, scale)

    bpy.ops.object.transform_apply(scale=True)
    mat = bpy.data.materials.new(name="body_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (0.8, 0.5, 0.4, 1.0)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return obj


def resize_objects(obj):
    """Resize the given object by a factor of 0.001."""
    scale_factor = 0.001
    obj.scale = (scale_factor, scale_factor, scale_factor)
    bpy.ops.object.transform_apply(scale=True)
    print(f"Resized object: {obj.name} to scale {obj.scale}")


def rotate_around_centroid(obj):
    """jj the given object around y and z axis by -180 degrees."""
    rot_y = math.radians(-90)
    rot_z = math.radians(-90)

    obj.rotation_euler[1] = rot_y  # Y軸
    obj.rotation_euler[2] = rot_z
    print(f"Rotated object: {obj.name}")


def set_origin_to_center_of_mass(obj):
    """Set the origin of the given object to its center of mass."""
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="MEDIAN")
    print(f"Set origin to center of mass for object: {obj.name}")
