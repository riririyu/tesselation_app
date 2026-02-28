import bpy
import os
import sys
import gmsh
import bmesh
import json
from pathlib import Path
import importlib

directory = Path(
    bpy.context.space_data.text.filepath if bpy.context.space_data.text else None
).parent
sys.path.append(str(directory))

my_modules = ["config", "utils", "dxf_pattern_processer", "pattern_processer", "sim"]


def reload_all():
    for mod_name in my_modules:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
            print(f"Reloaded: {mod_name}")


def main():
    reload_all()
    import config
    import utils
    import dxf_pattern_processer as dp
    import pattern_processer as pp
    import sim

    utils.purge_all_curves_and_meshes()
    with config.keypoints_filepath.open(mode="r", encoding="utf-8") as file:
        keypoints_data = json.load(file)
    # dp.visualize_split_points(keypoints_data, radius=5)

    with config.edge_filepath.open(mode="r", encoding="utf-8") as file:
        edge_data = json.load(file)

    utils.import_obj(config.smpl_joints_obj_filepath)

    dp.import_patterns(
        config.dxf_filepaths, config.keypoints_filepath, config.object_names
    )
    smpl_obj = utils.import_obj(config.smpl_obj_filepath)
    with config.smpl_joints_json_filepath.open(mode="r", encoding="utf-8") as file:
        joint_data = json.load(file)

    panel_objects = []
    for panel in list(config.object_names.values()):
        print(f"{panel} processing")
        bpy.context.view_layer.update()
        obj = bpy.data.objects.get(panel)
        split_points = dp.extract_split_points_from_index(obj, keypoints_data)
        split_points_names = dp.extract_split_points_names_from_keypoints(
            obj, keypoints_data
        )
        dp.split_curve(obj, split_points)
        # set stitch points on each curve
        pp.subdivide_curve(obj)

        pp.convert_to_mesh(obj)
        pp.create_faces(obj)
        print(f"{obj.name} remeshing...")
        pp.remesh_by_gmsh(obj, lc=100)
        pp.create_vertex_groups_for_edges(obj, split_points, split_points_names)
        # set fixed vertices
        if obj.name == "front_bodice_d":

            print("redifine curve and create vertex group for yoke")

        utils.resize_objects(obj)
        utils.rotate_around_centroid(obj)
        utils.set_origin_to_center_of_mass(obj)
        obj.location = (0, 0, 0)
        panel_objects.append(obj)

    for panel in list(config.object_mirror):
        obj = bpy.data.objects.get(panel)
        mirror_obj = pp.duplicate_and_mirror_objects(obj)
        panel_objects.append(mirror_obj)
    pp.bend_waistbelt("waist_belt")

    pp.locate_panel_obj_on_body(joint_data)
    return
    joined_obj = pp.join_all_mesh_objects(panel_objects)

    sim.flip_normal(smpl_obj, joined_obj)
    pp.create_edges_between_groups(joined_obj, edge_data)

    # シミュレーション設定
    sim.add_collision_modifier(smpl_obj)
    sim.apply_cloth_modifier(joined_obj)

    # simulate sewing

    # export_glb(glb_filepath)


if __name__ == "__main__":
    main()
