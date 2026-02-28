import torch
import smplx
import numpy as np
from smplx.joint_names import JOINT_NAMES
def set_body_pose(mode):
    if mode == 'A':
        body_pose[0, 15, 2] = -np.pi/4
        body_pose[0, 16 ,2] = np.pi/4  
    elif mode == 'Y':
        body_pose[0, 15, 2] = -np.pi/4
        body_pose[0, 16 ,2] = np.pi/4  
def mdfy_scale(verts, scale):
    verts *= scale
def save_obj(verts, faces, obj_mesh_name):
    with open(obj_mesh_name, 'w') as f:
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
def save_json(data, keys, filename):
    import json
    data_dict = {keys[i]: coord.tolist() for i, coord in enumerate(data)}
    with open(filename, 'w') as f:
        json.dump(data_dict, f, indent=4)

model_path = './models'  # モデルデータが格納されているディレクトリ
model = smplx.create(model_path, model_type='smplx',
                     gender='neutral', use_face_contours=True,
                     num_betas=10, num_expression_coeffs=10)

betas = torch.zeros([1, 10], dtype=torch.float32)
expression = torch.zeros([1, 10], dtype=torch.float32)
body_pose = torch.zeros([1, 21, 3], dtype=torch.float32)
set_body_pose('A') 

output = model(betas=betas, expression=expression, body_pose=body_pose, return_verts=True)

vertices = output.vertices[0].detach().cpu().numpy()
faces = model.faces
joints = output.joints[0].detach().cpu().numpy()


print(f" joints shape: {joints.shape}") 
print(f"JOINT NAMES shape: {len(JOINT_NAMES)}")
save_obj(vertices, faces, './smpl/smplx_output.obj')

save_obj(joints, [], './smpl/smplx_joints.obj')


save_json(joints,JOINT_NAMES,'./smpl/smplx_joints.json')


