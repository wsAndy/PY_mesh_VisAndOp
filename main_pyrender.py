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

isDebug = True if sys.gettrace() else False

# 纯色渲染参考：https://github.com/mmatl/pyrender/issues/51

# 干掉AA的一个trick操作：https://github.com/marian42/mesh_to_sdf/blob/66036a747e82e7129f6afc74c5325d676a322114/mesh_to_sdf/pyrender_wrapper.py#L20

class TriScene():
    def __init__(self):
        self.scene = pyrender.Scene(ambient_light = [1., 1., 1.])
        self.scene.bg_color = [0., 0., 0., 1.0]
        self.id = str(uuid.uuid1())
        self.mat = None
        self.mesh = None

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
            self.mesh = self.mesh.from_trimesh( fuze_trimesh, material=self.mat  )
        else:
            self.mesh = pyrender.Mesh.from_trimesh(fuze_trimesh, material=self.mat  )
        if self.mesh not in self.scene.meshes:
            self.scene.add(self.mesh)


    def addMat(self):
        self.mat = pyrender.MetallicRoughnessMaterial()
        self.mat.baseColorFactor = [0., 1., 1., 1.]

    def addCamera(self):
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
        camera_pose = np.array([[1.0, 0,    0.0,   0],
                                [0.0,  -1.0, 0.0, 0],
                                [0.0,  0.0,   -1,   -10],
                                [0.0,  0.0, 0.0, 1.0]])
        # TODO: pyrender的opengl坐标系，和blender坐标系的映射，一定有现成的
        self.scene.add(camera, pose=camera_pose)

class PYRender():
    def __init__(self):
        self.r = pyrender.OffscreenRenderer(viewport_width=640,
                                       viewport_height=480,
                                       point_size=1.0)

    def render(self, scene: pyrender.Scene):
        color, depth = self.r.render(scene, flags=pyrender.constants.RenderFlags.OFFSCREEN)
        return color, depth

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

if __name__ == '__main__':
    ut.initLog()

    logger.info("================================")

    rr = PYRender()

    s1 = TriScene()
    meshlab1 = LoadMeshFromPyMeshLab()
    # s1.addMesh(path=os.path.join(r"D:\assets\ico.obj"))
    meshlab1.loadMesh(os.path.join(r"D:\assets\suzanne.obj"))
    s1.addMesh(vertices=meshlab1.mesh.vertex_matrix(), faces=meshlab1.mesh.face_matrix() )
    s1.addCamera()

    s2 = TriScene()
    meshlab2 = LoadMeshFromPyMeshLab()
    # s2.addMesh(path=os.path.join(r"D:\assets\ico.obj"))
    meshlab2.loadMesh(os.path.join(r"D:\assets\ico.obj"))
    s2.addMesh(vertices=meshlab2.mesh.vertex_matrix(), faces=meshlab2.mesh.face_matrix() )
    s2.addCamera()

    # 下面的渲染配置可能是正确的
    for j in range(5):
        start_time = time.time()
        for i in [s1]:
            color, depth = rr.render(i.scene)

            duration = ( time.time() - start_time ) / 1
            logger.info(f'Duration = {duration}')

            im = Image.fromarray(color)
            im.save(f"pyrender_color_{j}_{i.id[:6]}.png")
        # do
        meshlab1.Dec()
        s1.addMesh(vertices=meshlab1.mesh.vertex_matrix(), faces=meshlab1.mesh.face_matrix() )
        if isDebug:
            print(meshlab1.mesh.vertex_matrix().shape[0])

    rr.destroy()