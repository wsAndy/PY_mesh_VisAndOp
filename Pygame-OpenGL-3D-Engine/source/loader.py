'''
模型加载
'''

import pymeshlab
import trimesh
import numpy as np
import os

# C:\Users\admin\Documents\suzanne.fbx
class ModelLoader():
    def __init__(self):
        self.meshSet = pymeshlab.MeshSet()

        self.blender2opengl = np.array([ [1, 0, 0], [0, 0, 1], [0, -1, 0]])

    def load(self, path, type="blender"):
        self.meshSet.clear()
        self.meshSet.load_new_mesh(path)
        # self.meshSet.get_geometric_measures()
        self.meshSet.compute_texcoord_transfer_wedge_to_vertex()
        highMesh = self.meshSet.current_mesh()
        highMesh.compact()

        # if type == "blender":
        # vertexArray = np.matmul(highMesh.vertex_matrix(), self.blender2opengl)

        vertexArray = highMesh.vertex_matrix()

        # (faceNum*3, 2), 记录每一个三角形中每一个顶点的uv
        # meshlab读取后，相当于rts是单位阵，所有变化都到顶点去了
        return { "vertices":vertexArray, "faces":highMesh.face_matrix(), "uv": highMesh.vertex_tex_coord_matrix()   }

    def load2trimesh(self, path):
        res = self.load(path)
        return trimesh.Trimesh(vertices=res["vertices"], faces=res["faces"] )

