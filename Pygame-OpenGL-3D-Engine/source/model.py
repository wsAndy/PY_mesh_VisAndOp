import glm
import numpy as np
import pygame

from source.engine import Engine

from source.actor import Actor

import moderngl


class GlobalAxes(Actor):
    def __init__(self, app: Engine):
        super().__init__()
        self.app = app
        self.ctx = self.app.ctx
        self.camera = self.app.camera
        # 定义顶点数据和索引
        self.verticesX = np.array([
            0.0, 0.0, 0.0,  # 原点
            self.camera.m_farPlane, 0.0, 0.0,  # X轴
        ], dtype='f4')
        self.verticesY = np.array([
            0.0, 0.0, 0.0,  # 原点
            0.0, self.camera.m_farPlane, 0.0,  # Y轴
        ], dtype='f4')
        self.verticesZ = np.array([
            0.0, 0.0, 0.0,  # 原点
            0.0, 0.0, self.camera.m_farPlane,  # Z轴
        ], dtype='f4')

        self.indices = np.array([0, 1], dtype='i4')
        self.ibo = self.ctx.buffer(self.indices)

        self.vboX = self.ctx.buffer(self.verticesX)
        self.vboY = self.ctx.buffer(self.verticesY)
        self.vboZ = self.ctx.buffer(self.verticesZ)

        self.colorBufferRed = self.ctx.buffer( np.array([1, 0, 0, 1, 0, 0], dtype='f4') )
        self.colorBufferGreen = self.ctx.buffer(np.array([0, 1, 0, 0, 1, 0], dtype='f4'))
        self.colorBufferBlue = self.ctx.buffer(np.array([0, 0, 1, 0, 0, 1], dtype='f4'))

        # 创建着色器程序
        self.prog = self.ctx.program(
            vertex_shader = '''
                #version 330
                uniform mat4 Mvp;
                layout (location=0) in vec3 in_vert;
                layout (location=1) in vec3 in_color;
                out vec3 v_color;
                void main() {
                    v_color = in_color; 
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader = '''
                #version 330
                out vec4 f_color;
                in vec3 v_color;
                void main() {
                    f_color = vec4(v_color, 1.0);
                }
            ''',
        )

        # 设置顶点属性
        self.vaoX = self.ctx.vertex_array(
            program=self.prog,
            content=[
                (self.vboX, '3f', 'in_vert'),
                (self.colorBufferRed, '3f', 'in_color')
            ],
            index_buffer=self.ibo
        )
        self.vaoY = self.ctx.vertex_array(
            program=self.prog,
            content=[
                (self.vboY, '3f', 'in_vert'),
                (self.colorBufferGreen, '3f', 'in_color')
            ],
            index_buffer=self.ibo
        )
        self.vaoZ = self.ctx.vertex_array(
            program=self.prog,
            content=[
                (self.vboZ, '3f', 'in_vert'),
                (self.colorBufferBlue, '3f', 'in_color')
            ],
            index_buffer=self.ibo
        )

    def tick(self):
        mvp = self.camera.projection_matrix() * self.camera.view_matrix()
        self.prog['Mvp'].write(mvp)
        oriLineWidth = self.ctx.line_width
        self.ctx.line_width = 3
        self.vaoX.render(moderngl.LINES)
        self.vaoY.render(moderngl.LINES)
        self.vaoZ.render(moderngl.LINES)
        self.ctx.line_width = oriLineWidth

    def destroy(self):
        super().destroy()
        self.vboX.release()
        self.vboY.release()
        self.vboZ.release()

        self.vaoX.release()
        self.vaoY.release()
        self.vaoZ.release()

        self.colorBufferRed.release()
        self.colorBufferGreen.release()
        self.colorBufferBlue.release()

        self.prog.release()
        self.ibo.release()

class Triangle:
    def __init__(self, app: Engine):
        self.app = app
        self.ctx = self.app.ctx
        self.camera = self.app.camera
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program(
            "default.vert", "default.frag"
        )
        self.vao = self.get_vao()

        self.shader_program['projection_matrix'].write(
            self.camera.projection_matrix()
        )
        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        )

        self.model_matrix = self.get_model_matrix()
        self.shader_program['model_matrix'].write(
            self.model_matrix
        )

    def get_model_matrix(self):
        return glm.mat4()

    def update(self):
        model_matrix = glm.rotate(
            self.model_matrix, self.app.time, glm.vec3(0.0, 1.0, 0.0)
        )
        self.shader_program['model_matrix'].write(model_matrix)

        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        ) 

    def tick(self):
        print('not follow camera')
        # self.update()
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        return self.ctx.vertex_array(
            self.shader_program,
            [(self.vbo, '3f', 'in_position')],
        )

    def get_vertex_data(self):
        return np.array([
            0, 60, 0.0,
            0.0, -10, -10.0,
            100, 0, 0.0,
        ], dtype='f4')

    def get_vbo(self):
        return self.ctx.buffer(self.get_vertex_data())

    def get_shader_program(self, vertex_shader: str, fragment_shader: str):
        with open(f"source/shaders/{vertex_shader}") as f:
            vertex_code = f.read()

        with open(f"source/shaders/{fragment_shader}") as f:
            fragment_code = f.read()

        return self.ctx.program(
            vertex_shader=vertex_code,
            fragment_shader=fragment_code,
        )


class Cube:
    def __init__(self, app: Engine):
        self.app = app
        self.ctx = self.app.ctx
        self.camera = self.app.camera
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program(
            "default.vert", "default.frag"
        )
        self.vao = self.get_vao()
 
        # Load texture
        self.texture = self.get_texture("assets/textures/wood.png")

        # Set texture
        self.shader_program['texture_0'] = 0
        self.texture.use()

        self.shader_program['projection_matrix'].write(
            self.camera.projection_matrix()
        )
        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        )

        self.model_matrix = self.get_model_matrix()
        self.shader_program['model_matrix'].write(
            self.model_matrix
        )

    def get_texture(self, path: str):
        texture = pygame.image.load(path).convert()
        texture = pygame.transform.flip(texture, False, True)
        texture_data = pygame.image.tostring(texture, "RGB")
        return self.ctx.texture(texture.get_size(), 3, texture_data)

    def get_model_matrix(self):
        return glm.mat4()

    def update(self):
        model_matrix = glm.rotate(
            self.model_matrix, self.app.time * 0.5, glm.vec3(0.0, 1.0, 0.0)
        )
        self.shader_program['model_matrix'].write(model_matrix)

        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        ) 

    def tick(self):
        self.update()
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        return self.ctx.vertex_array(
            self.shader_program,
            [(self.vbo, '2f 3f', 'in_text_coord_0', 'in_position')],
        )

    def get_vertex_data(self):
        vertices = [
            (1.0, -1.0, -1.0), (1.0, 1.0, -1.0), (-1.0,
                                                  1.0, -1.0), (-1.0, -1.0, -1.0),  # front
            (1.0, -1.0, 1.0), (1.0, 1.0, 1.0), (-1.0, - \
                                                1.0, 1.0), (-1.0, 1.0, 1.0),  # back
        ]

        indices = [
            (0, 1, 2), (0, 2, 3),  # front
            (4, 6, 5), (5, 6, 7),  # back
            (0, 3, 6), (0, 6, 4),  # left
            (1, 5, 2), (5, 7, 2),  # right
            (3, 2, 7), (3, 7, 6),  # top
            (0, 4, 1), (1, 4, 5),  # bottom
        ]

        # Texture coordinates
        tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]

        tex_coord_indices = [
            (0, 3, 2), (0, 2, 1),  # back (done)
            (1, 0, 2), (2, 0, 3),  # front (done)
            (0, 1, 2), (0, 2, 3),  # bottom (done)
            (2, 1, 3), (1, 0, 3),  # top (done)
            (0, 3, 2), (0, 2, 1),  # left (done)
            (1, 0, 2), (2, 0, 3),  # right (done)
        ]

        # Texture coordinate data
        tex_coord_data = np.array(
            [tex_coords[i] for j in tex_coord_indices for i in j], dtype='f4'
        )

        vertex_data = np.array([
            vertices[i] for triangle in indices for i in triangle  # flatten
        ], dtype='f4')

        return np.hstack([tex_coord_data, vertex_data])

    def get_vbo(self):
        return self.ctx.buffer(self.get_vertex_data())

    def get_shader_program(self, vertex_shader: str, fragment_shader: str):
        with open(f"source/shaders/{vertex_shader}") as f:
            vertex_code = f.read()

        with open(f"source/shaders/{fragment_shader}") as f:
            fragment_code = f.read()

        return self.ctx.program(
            vertex_shader=vertex_code,
            fragment_shader=fragment_code,
        )


from source.loader import ModelLoader
from source.components.transformComp import TransformComponent

class CustomMesh(Actor):
    def __init__(self, app: Engine):
        super().__init__()
        self.modelLoader = ModelLoader()
        self.app = app
        self.ctx = self.app.ctx
        self.camera = self.app.camera
        self.shader_program = self.get_shader_program(
            "default.vert", "default.frag"
        )
        self.STATE=0
        # Load texture
        self.texture = self.get_texture("assets/textures/test.png")

        # initialize
        self.pos_vbo = None
        self.coords_vbo = None
        self.vao = None
        self.ibo = None

        # Set texture
        self.shader_program['texture_0'] = 0
        self.texture.use()

        self.shader_program['projection_matrix'].write(
            self.camera.projection_matrix()
        )
        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        )

        self.model_matrix = self.get_model_matrix()
        self.shader_program['model_matrix'].write(
            self.model_matrix
        )

    def loadModel(self, path):
        self.STATE=0
        if self.pos_vbo:
            self.pos_vbo.release()
        if self.coords_vbo:
            self.coords_vbo.release()
        if self.ibo:
            self.ibo.release()

        self.loadedMesh = self.modelLoader.load(path)
        self.pos_vbo = self.ctx.buffer( self.loadedMesh['vertices'].astype('f4').tobytes() )
        self.coords_vbo = self.ctx.buffer( self.loadedMesh['uv'].astype('f4').tobytes() )
        self.ibo =self.ctx.buffer( self.loadedMesh['faces'].tobytes() )

        self.vao = self.ctx.vertex_array(
            program = self.shader_program,
            content= [
                (self.coords_vbo, '2f', 'in_text_coord_0' ),
                (self.pos_vbo, '3f', 'in_position'),
            ],
            index_buffer = self.ibo
        )
        self.STATE=1

        # 物体的local坐标系，现在和opengl 右手系保持一致
        # self.transformComponent.location = glm.vec3( 0, 0, 0)

        # ## 顺时针为正
        # # 输入ue ypr
        # yaw,pitch,roll = self.leftHand2RightHand(202.862775, 173.8452, 149.172)
        # ## 注意,从UE过来,经过坐标系变换,物体rot计算顺序为yaw\roll\pitch
        # self.transformComponent.yaw(yaw)
        # self.transformComponent.roll(roll)
        # self.transformComponent.pitch(pitch)

        # self.transformComponent.yaw(45)
        # self.transformComponent.roll(-45)
        # self.transformComponent.pitch(-45)

    def leftHand2RightHand(self, yaw, pitch, roll):
        return yaw, -roll, -pitch

    def get_texture(self, path: str):
        texture = pygame.image.load(path).convert()
        texture = pygame.transform.flip(texture, False, True)
        texture_data = pygame.image.tostring(texture, "RGB")
        return self.ctx.texture(texture.get_size(), 3, texture_data)

    def get_model_matrix(self):
        return glm.mat4()

    def update(self):
        # model_matrix = glm.rotate( self.model_matrix, self.app.time * 0.5, glm.vec3(0.0, 1.0, 0.0) )

        scale = glm.scale(self.transformComponent.scale)
        rotation = glm.transpose(self.transformComponent.rotation())
        translation = glm.translate(self.transformComponent.location)

        model_matrix = translation * rotation * scale

        # print('------ model ------')
        # print(self.transformComponent.forward())
        # print(self.transformComponent.up())
        # print(self.transformComponent.right())
        

        self.shader_program['model_matrix'].write(model_matrix)

        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        ) 

    def tick(self):
        if self.STATE != 0:
            super().tick()
            self.update()
            self.vao.render()

    def destroy(self):
        if self.pos_vbo:
            self.pos_vbo.release()
        if self.coords_vbo:
            self.coords_vbo.release()
        if self.ibo:
            self.ibo.release()
        self.shader_program.release()
        if self.vao:
            self.vao.release()

    def get_shader_program(self, vertex_shader: str, fragment_shader: str):
        with open(f"source/shaders/{vertex_shader}") as f:
            vertex_code = f.read()

        with open(f"source/shaders/{fragment_shader}") as f:
            fragment_code = f.read()

        return self.ctx.program(
            vertex_shader=vertex_code,
            fragment_shader=fragment_code,
        )
    
     