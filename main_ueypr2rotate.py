
import os
import trimesh.transformations as transf
import numpy as np

np.set_printoptions(suppress = True)

from scipy.spatial.transform import Rotation as R

# Pitch=23.039937
# Yaw=32.639909
# Roll=30.719911

# uerot = np.asarray(
#   [[0.774906, 0.496334, 0.391373 , 0],
#   [-0.295316, 0.831746, -0.470093, 0],
#   [-0.558846, 0.248699, 0.791101, 0],
#   [0, 0, 0, 1]  
# ])


Pitch=39.599889
Yaw=277.439221
Roll=81.119784

uerot = np.asarray([
    [0.0997619, -0.764029, 0.637422, 0],
    [0.234611 ,-0.604494, -0.761278, 0], 
    [0.966957, 0.225493, 0.118944, 0],
    [0, 0, 0, 1]  
])

def deg2rad(x):
    return x*3.14159/180.0

def getUERotMatrix(Roll, Pitch, Yaw):
    # 等同于：R.from_euler('xyz', [Roll, Pitch, Yaw], degrees=True).as_matrix()
    rotmat = transf.euler_matrix( deg2rad(Roll), deg2rad(Pitch), deg2rad(Yaw), 'sxyz')
    rotmat[2,:3] = rotmat[2,:3]*-1
    rotmat[:,2] = rotmat[:,2]*-1
    rotmat = rotmat.transpose()
    print(rotmat)
    return rotmat[:3,:3]

    # print( np.linalg.inv(uerot[:3,:3]) * rotmat[:3,:3] )

# getUERotMatrix(Roll, Pitch, Yaw)
yaws = [20] # roll
pitchs = [ 45] #, 45, 90, 135, 180, 225] # yaw
rolls = [0, 20, 30, 45, 60, 90, 120, 150 , 180] # pitch

for yaw in yaws:
    for pitch in pitchs:
        for roll in rolls:
            print(f'======================{yaw}, {pitch}, {roll}')
            getUERotMatrix(roll, pitch, yaw)
