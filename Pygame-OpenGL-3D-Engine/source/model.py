import glm
import numpy as np
from source.actor import Actor
from source.loader import ModelLoader
import os
import moderngl


class GlobalAxes(Actor):
    def __init__(self, app):
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

class CustomMesh(Actor):
    def __init__(self, app):
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
        self.texture = self.get_texture( os.path.join( self.app.resource_dir, "textures/test.png") )

        # initialize
        self.pos_vbo = None
        self.coords_vbo = None
        self.vao = None
        self.ibo = None

        self.model_matrix = self.get_model_matrix()
        self.shader_program['model_matrix'].write(
            self.model_matrix
        )
        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        )
        self.shader_program['projection_matrix'].write(
            self.camera.projection_matrix()
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
        ## 可以直接使用setYPR接口
        # # yaw,pitch,roll=model2.leftHand2RightHand(10, 20, 30)
        # # model2.transformComponent.setYPR(yaw, pitch, roll)

    def leftHand2RightHand(self, yaw, pitch, roll):
        return yaw, -roll, -pitch

    def get_texture(self, path: str):
        return self.app.load_texture_2d(path)

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

        self.texture.use(location=0)
        self.shader_program['texture_0'] = 0

        self.shader_program['model_matrix'].write(model_matrix)
        self.shader_program['view_matrix'].write(
            self.camera.view_matrix()
        )
        self.shader_program['projection_matrix'].write(
            self.camera.projection_matrix()
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
        with open( os.path.join( self.app.shader_dir, f"{vertex_shader}"), "r" )as f:
            vertex_code = f.read()

        with open( os.path.join( self.app.shader_dir, f"{fragment_shader}"), "r" )as f:
            fragment_code = f.read()

        return self.ctx.program(
            vertex_shader=vertex_code,
            fragment_shader=fragment_code,
        )
    
     