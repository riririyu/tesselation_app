import bpy
from pathlib import Path

directory = Path(
    bpy.context.space_data.text.filepath if bpy.context.space_data.text else None
).parent.parent

dxf_filepaths = [
    Path(directory / "input" / "BET-30-680-32.ウエストベルト.dxf"),
    Path(directory / "input" / "BET-30-680-32.前身頃D.dxf"),
    Path(directory / "input" / "BET-30-680-32.ヨーク.dxf"),
    Path(directory / "input" / "BET-30-680-32.後身頃.dxf"),
]
keypoints_filepath = Path(directory / "input" / "2026_2_14_修正版_keypoints.json")
edge_filepath = Path(directory / "input" / "edge.json")
smpl_obj_filepath = Path(directory / "input" / "smpl" / "smplx_output.obj")
smpl_joints_json_filepath = Path(directory / "input" / "smpl" / "smplx_joints.json")
smpl_joints_obj_filepath = Path(directory / "input" / "smpl" / "smplx_joints.obj")
glb_filepath = Path(directory / "output" / "BET-30-680-32.glb")
object_names = {
    "後身頃": "back_bodice",
    "前身頃D": "front_bodice_d",
    "ヨーク": "yoke",
    "ウエストベルト": "waist_belt",
}
object_mirror = {
    "back_bodice",
    "front_bodice_d",
    "yoke",
}
SIMULATION_FRAMES = 30
SIMULATION_QUALITY = 10
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
    "pin_group": "fixed_vertices",
    "self_distance_min": 0.02,
    "use_collision": True,
    "friction": 0.0,
}
SMPL_SETTINGS = {
    "scale": (1, 1, 1),
    "location_offset": (0, 0, 0),
    "material_color": (0.0, 0.0, 0.0),
}
MATERIAL_SETTINGS = {
    "default_color": (0.8, 0.8, 0.8, 1.0),
    "default_roughness": 0.5,
    "default_metallic": 0.0,
}
SEWING_SETTINGS = {"num_stitch": 20}
GRAVITY = (0, 0, -9.81)
