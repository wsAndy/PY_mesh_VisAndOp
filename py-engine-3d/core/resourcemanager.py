'''
统一管理所有加载的资产，如
mesh、texture、material (shader)
''''''
模型加载
'''

import moderngl
import pymeshlab
import trimesh
import numpy as np
from core.materials import BaseMaterial
from core.materials import CustomMaterial
import glm
from core.actor import Actor

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


class Mesh(Actor):
    _mat = None
    _vertices = None
    _faces = None
    _uv = None
    _isChanged = False

    # initialize
    _pos_vbo = None
    _coords_vbo = None
    _vao = None
    _ibo = None

    # 映射shader需要的uv、position
    shaderMap = {'uv': 'in_text_coord_0', 'posiiton': 'in_position'}

    def __init__(self, ctx, vertices=None, faces = None, uv = None, mat = None):
        super().__init__()
        self.ctx = ctx
        if vertices is not None:
            self.setVertices(vertices)
        if faces  is not  None:
            self.setFaces(faces)
        if uv  is not None:
            self.setUV(uv)
        if mat  is not  None:
            self.setMat(mat)

    
    def leftHand2RightHand(self, yaw, pitch, roll):
        '''
        物体的local坐标系，现在和opengl 右手系保持一致
        self.transformComponent.location = glm.vec3( 0, 0, 0)
        ## 顺时针为正
        # 输入ue ypr
        yaw,pitch,roll = self.leftHand2RightHand(202.862775, 173.8452, 149.172)

        ## 注意,从UE过来,经过坐标系变换,物体rot计算顺序为yaw\roll\pitch
        self.transformComponent.yaw(yaw)
        self.transformComponent.roll(roll)
        self.transformComponent.pitch(pitch)

        # 可以直接使用setYPR接口
        yaw,pitch,roll=model2.leftHand2RightHand(10, 20, 30)
        model2.transformComponent.setYPR(yaw, pitch, roll)
        '''
        return yaw, -roll, -pitch

    def tick(self, ):
        '''
        do tick
        '''
        super().tick()
        self._render()

        self.isChanged = False

    def getMatId(self,):
        if self._mat is not None:
            return self._mat.id
        else:
            return ""
    def getMat(self,):
        return self._mat
    def setMat(self, mat):
        self._mat = mat
        self._isChanged = True

    def setVertices(self, v):
        self._vertices = v
        if self._pos_vbo is not None:
            self._pos_vbo.release()
        self._pos_vbo = self.ctx.buffer( v.astype('f4').tobytes() )
        self._isChanged = True

    def setFaces(self, f):
        self._faces = f
        if self._ibo is not None:
            self._ibo.release()
        self._ibo = self.ctx.buffer( f.tobytes() )
        self._isChanged = True

    def setUV(self, uv):
        self._uv = uv
        if self._coords_vbo is not None:
            self._coords_vbo.release()
        self._coords_vbo = self.ctx.buffer( uv.astype('f4').tobytes() )
        self._isChanged = True

    def _updateVAO(self,):
        if self._vao is not None:
            self._vao.release()
        if self._mat.isReady() and self._coords_vbo and self._pos_vbo and self._ibo:
            self._vao = self.ctx.vertex_array(
                program = self._mat.shader_program,
                content= [
                    (self._coords_vbo, '2f', self.shaderMap['uv'] if 'uv' in self.shaderMap else 'in_text_coord_0' ),
                    (self._pos_vbo, '3f', self.shaderMap['position'] if 'position' in self.shaderMap else 'in_position' ),
                ],
                index_buffer = self._ibo
            ) 
        else:
            self._vao = None

    def _render(self, ):
        '''rendering 
        vao的渲染
        '''
        if self._vao is None:
            self._updateVAO()
        
        # 如果依然是None，不渲染
        if self._vao is None:
            return
        
        scale = glm.scale(self.transformComponent.scale)
        rotation = glm.transpose(self.transformComponent.rotation())
        translation = glm.translate(self.transformComponent.location)
        model_matrix = translation * rotation * scale

        # 此时保证self._mat.shader_program有值
        self._mat.shader_program['model_matrix'].write(model_matrix)
        # 贴图分配
        for texId in self._mat.textures:
            _tex = self._mat.textures[texId]
            _shaderTexName = self._mat.texturesMap[texId]
            _tex.use(location= texId)
            self._mat.shader_program[_shaderTexName] = texId
            
        self._vao.render()
        

    

class ResourceManager:

    meshes: list[Mesh] = []
    materials: list[BaseMaterial] = []
    shaders: list[moderngl.Program] = []
    texture2Ds: list[moderngl.Texture] = []
    textureCubes: list[moderngl.TextureCube] = []
    texture3Ds: list[moderngl.Texture3D] = []

    def __init__(self, manager) -> None:
        self.sm = manager
        self.changed = False
        pass

    def isChanged(self,):
        '''
        TODO: 检查状态是否发生变化

        模型变化、材质变化、灯光变化，都需要change
        '''
        return self.changed
        

    def loadMesh(self, path):
        '''
        加载指定path的模型
        先不考虑mesh本身带有材质的情况
        '''
        # TODO: 加载path路径下的文件, 修改加载的逻辑
        mm = ModelLoader()
        info = mm.load(path)
        tmp = Mesh(ctx = self.sm.ctx, vertices=info['vertices'], faces=info['faces'], uv=info['uv'])
        self.meshes.append(tmp)
        self.changed = True
        return tmp
    
    def createCustomMaterial(self, vertex_path: str, fragment_path: str):
        '''
        创建自定义材质
        '''
        sp = self.loadProgram(vertex_path, fragment_path)
        tmp = CustomMaterial(sp)
        self.materials.append(tmp)
        return tmp

    def loadProgram(self, vertex_path: str, fragment_path: str):
        '''
        加载shader
        '''
        tmp = self.sm.load_program(vertex_shader=vertex_path, fragment_shader=fragment_path)
        self.shaders.append(tmp)
        return tmp
    
    def loadTexture2D(self, path):
        tmp = self.sm.load_texture_2d(path)
        self.texture2Ds.append(tmp)
        return tmp

    def loadTexture3D(self, path):
        tmp = self.sm.load_texture_3d(path)
        self.texture3Ds.append(tmp)
        return tmp
    
    def loadTextureCube(self, path):
        tmp = self.sm.load_texture_cube(path)
        self.textureCubes.append(tmp)
        return tmp
