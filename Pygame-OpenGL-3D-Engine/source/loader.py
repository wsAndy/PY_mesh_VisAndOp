'''
模型加载
'''

import pymeshlab
import trimesh
import os

# C:\Users\admin\Documents\suzanne.fbx
class ModelLoader():
    def __init__(self):
        self.meshSet = pymeshlab.MeshSet()

    def load(self, path):
        self.meshSet.clear()
        self.meshSet.load_new_mesh(path)
        # self.meshSet.get_geometric_measures()
        highMesh = self.meshSet.current_mesh()
        # (faceNum*3, 2), 记录每一个三角形中每一个顶点的uv
        return { "vertices":highMesh.vertex_matrix(), "faces":highMesh.face_matrix(), "uv": highMesh.wedge_tex_coord_matrix()   }

    def load2trimesh(self, path):
        res = self.load(path)
        return trimesh.Trimesh(vertices=res["vertices"], faces=res["faces"] )

