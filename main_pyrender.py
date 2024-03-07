import sys
import os
import utils_ws as ut
from loguru import logger
import numpy as np
import time
import uuid

import pymeshlab
import pyrender
import trimesh
from PIL import Image
import math

np.set_printoptions(suppress = True)

isDebug = True if sys.gettrace() else False

# 纯色渲染参考：https://github.com/mmatl/pyrender/issues/51

# 干掉AA的一个trick操作：https://github.com/marian42/mesh_to_sdf/blob/66036a747e82e7129f6afc74c5325d676a322114/mesh_to_sdf/pyrender_wrapper.py#L20

# 自定义shader的实验：https://github.com/mmatl/pyrender/issues/39

class TriScene():
    def __init__(self):
        self.scene = pyrender.Scene(ambient_light = [1., 1., 1.])
        self.scene.bg_color = [0., 0., 0., 1.0]
        self.id = str(uuid.uuid1())
        self.mat = None
        self.mesh = None
        self.cameraNode = None

    def addMesh(self, path = None, vertices = None, faces = None):
        if self.mat is None:
            self.addMat()

        if path is not None:
            fuze_trimesh = trimesh.load(path)
        elif vertices is not None and faces is not None:
            fuze_trimesh = trimesh.Trimesh(vertices=vertices,
                               faces=faces)
        else:
            return

        if self.mesh is not None:
            self.mesh = self.mesh.from_trimesh( fuze_trimesh, material=self.mat, smooth=False )
        else:
            self.mesh = pyrender.Mesh.from_trimesh(fuze_trimesh, material=self.mat , smooth=False )
        if self.mesh not in self.scene.meshes:
            self.scene.add(self.mesh)


    def addMat(self):
        self.mat = pyrender.MetallicRoughnessMaterial()
        self.mat.baseColorFactor = [0., 1., 1., 1.]
 
    def addCamera(self, yaw = 0, pitch = 0, roll = 0, x =0,y=0,z=0):

        def deg2rad(x):
            return x * math.pi / 180.0
        
        def ueypr2opengl(yaw, pitch,roll):
            return 270 - yaw, pitch, -roll
        def ueloc2opengl(x,y,z):
            return x, z, y
        
        yaw, pitch, roll = ueypr2opengl(yaw, pitch, roll)
        x,y,z = ueloc2opengl(x,y,z)

        ## 这边指定的szxy的顺序，是world 的坐标轴的顺序
        rotmat = trimesh.transformations.euler_matrix( deg2rad(roll), deg2rad(pitch), deg2rad(yaw), 'szxy')
        '''
        终于清楚了，在做yaw、pitch、roll的旋转映射时，可以根据目标坐标系的ypr的计算顺序、坐标轴向顺序，得到相对相机主方向各个轴的旋转顺序。

        UE: 镜头看向X, 右侧是Y轴, 垂直向上是Z轴. 计算顺序是下图123:yaw、pitch、roll
        ^ yaw(1)  Z 
        |  
        |
        |------> roll(3)  X 
        \
         \
          v  pitch(2)  Y

        pyrender: 镜头看向 -Z, 右侧是X轴, 垂直向上是Y轴.
        ^ Y
        |  
        |
        |------> X 
        \
         \
          v  Z
        
        要做ue转pyrender(opengl), 首先我们确定旋转计算顺序。相对镜头的主方向而言, 在pyrender中, 先计算Y, 再计算X,在计算Z. 所以对于pyrender, 轴向为 'sxzy'

        '''
        camera_pose = np.eye(4)
        camera_pose[:3, :3] = rotmat[:3,:3]
        camera_pose[:3, 3] = [x,y,z]

        logger.info("================================")
        logger.info(f'{yaw}_{pitch}_{roll}')
        logger.info(rotmat)

        if self.cameraNode is None:
            camera = pyrender.PerspectiveCamera(yfov=np.pi / 2, aspectRatio=1.0)
            self.cameraNode = self.scene.add( camera, pose=camera_pose)
        else:
            self.cameraNode.matrix = camera_pose

    # def fromUEYPR2PyrenderPose(self, yaw = 0, pitch = 0, roll = 0):


class PYRender():
    def __init__(self):
        self.r = pyrender.OffscreenRenderer(viewport_width=512,
                                       viewport_height=512,
                                       point_size=1.0)

    def render(self, scene: pyrender.Scene):
        color, depth = self.r.render(scene, flags=pyrender.constants.RenderFlags.OFFSCREEN | pyrender.constants.RenderFlags.FACE_NORMALS)
        # rgb_normals_data, _ = self.r._renderer._read_main_framebuffer(scene, flags=pyrender.constants.RenderFlags.FACE_NORMALS)                                                      
        return color, depth #, rgb_normals_data

    def destroy(self):
        self.r.delete()

class LoadMeshFromPyMeshLab():
    def __init__(self):
        pass
    def loadMesh(self, path):
        self.meshSet = pymeshlab.MeshSet()
        # load high mesh
        self.meshSet.load_new_mesh(path)
        self.mesh = self.meshSet.current_mesh()

        # highMeshGeometric = meshSet.get_geometric_measures()

        if isDebug:
            vertNum = self.mesh.vertex_number()
            faceNum = self.mesh.face_number()
            logger.info(f'{path} has {vertNum} verts, {faceNum} faces.')

        self.meshSet.meshing_poly_to_tri()  # 先转换为纯三角网格
        # 减面之前先对模型做一次清理
        # meshSet.meshing_merge_close_vertices()  # threshold value is 1/10000 of bounding box diagonal
        self.meshSet.meshing_remove_duplicate_vertices()
        self.meshSet.meshing_remove_duplicate_faces()
        self.meshSet.meshing_remove_folded_faces()
        self.meshSet.meshing_remove_null_faces()
        self.meshSet.meshing_remove_unreferenced_vertices()

        return self.mesh
    def Dec(self):
        self.meshSet.meshing_decimation_quadric_edge_collapse(
            targetperc = 0.9, qualitythr = 0.3, preserveboundary=False, preservenormal=True,
            preservetopology=False, optimalplacement=True, planarquadric=True, planarweight=0.001,
            autoclean=False, selected=False
        )

def ue2render(yaw, pitch, roll):

    return yaw-90, pitch, -roll

if __name__ == '__main__':

    # # # Camera coordinate definition -- Following the CV convention, x-right, y-down, z-forward.

    # meshlab1 = LoadMeshFromPyMeshLab()
    # s1 = TriScene()
    # meshlab1.loadMesh(os.path.join(r"D:\data\axes.fbx"))
    # s1.addMesh(vertices=meshlab1.mesh.vertex_matrix(), faces=meshlab1.mesh.face_matrix() )
    # pyrender.Viewer(s1.scene, use_raymond_lighting=True)
    
    
    ut.initLog()

    logger.info("================================")

    ## 这边输入都是ue坐标系了
    x = 100
    y = 45
    z = 10
    yaws = [30]
    pitchs = [40]
    rolls = [80]

    rr = PYRender()

    s1 = TriScene()
    meshlab1 = LoadMeshFromPyMeshLab()
    # s1.addMesh(path=os.path.join(r"D:\assets\ico.obj"))
    meshlab1.loadMesh(os.path.join(r"D:\data\axes.fbx"))
    s1.addMesh(vertices=meshlab1.mesh.vertex_matrix(), faces=meshlab1.mesh.face_matrix() )

    for yaw in yaws:
        for pitch in pitchs:
            for roll in rolls:
                s1.addCamera(yaw=yaw, pitch=pitch, roll=roll, x= x,y=y,z=z)

                start_time = time.time()
                for i in [s1]:
                    color, depth = rr.render(i.scene)

                    duration = ( time.time() - start_time ) / 1
                    logger.info(f'Duration = {duration}')

                    im = Image.fromarray(color)
                    # im.save(f"pyrender_color_{j}_{i.id[:6]}.png")
                    im.save(f"{yaw}_{pitch}_{roll}_{x}_{y}_{z}.jpg")
                # # do
                # meshlab1.Dec()
                # s1.addMesh(vertices=meshlab1.mesh.vertex_matrix(), faces=meshlab1.mesh.face_matrix() )
                # if isDebug:
                #     print(meshlab1.mesh.vertex_matrix().shape[0])

    rr.destroy()
