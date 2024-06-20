'''
主入口，持有
resourcemanager
tick
UI
'''
import moderngl_window as mglw
from .ui import UI
from pathlib import Path
import moderngl
from .glcamera import GLCamera
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from .resourcemanager import ResourceManager

import os

class SceneManager(mglw.WindowConfig):
    gl_version = (4, 6)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent / '../assets').resolve()

    SPEED = 1000
    SENSITIVITY = 0.1

    frameNumber = 0
    rtWindowWidth = 512
    rtWindowHeight = 512


    # 当前次渲染队列
    renderLists = {} # key: material.id, values: list[Mesh] 
    renderListsMat = {} # key: material.id, values: material

    # 渲染前做资源分配
    def beforeRender(self,):
        '''
        检查下，如果 renderLists没有变化，则不需要重新装配
        否则，需要装配
        '''
        if self.resourcemanager.isChanged():
            self.renderLists = {}
            self.renderListsMat = {}
            '''
            重新做装配
            '''
            for mesh in self.resourcemanager.meshes:
                # 根据材质id做分配
                matId = mesh.getMatId()
                if matId in self.renderLists:
                    self.renderLists[matId].append(mesh)
                else:
                    self.renderLists[matId] = [mesh]
                # 根据材质id做分配
                if matId not in self.renderListsMat:
                    self.renderListsMat[matId] = mesh.getMat()
            pass
        pass

    def afterRender(self,):
        self.resourcemanager.changed = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = UI(self)

        self.camera = GLCamera()
        self.resourcemanager = ResourceManager(self)

        if self.rtWindowWidth is None:
            self.rtWindowWidth = 512
        if self.rtWindowHeight is None:
            self.rtWindowHeight = 512

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((self.rtWindowWidth, self.rtWindowHeight), 4),
            depth_attachment=self.ctx.depth_texture((self.rtWindowWidth, self.rtWindowHeight)),
        )
        self.camera.resize(self.rtWindowWidth, self.rtWindowHeight)

        
        self.imgui = ModernglWindowRenderer(self.wnd)

        # Ensure imgui knows about this texture
        # This is the color layer in the framebuffer
        self.imgui.register_texture(self.fbo.color_attachments[0])

        self.mouseLeftPress = False
        self.mouseRightPress = False
        self.qweasd = {'Q': False, 'W': False, 'E':False, 'A':False, 'S':False, 'D': False }

        '''
        TODO: 下面这一堆，需要单独剥离出来放到main外部
        '''
        mesh = self.resourcemanager.loadMesh( os.path.join(self.resource_dir, "models", "axes.fbx") )
        mat = self.resourcemanager.createCustomMaterial(vertex_path = os.path.join(self.resource_dir, "shaders", "default.vert" ), fragment_path = os.path.join(self.resource_dir, "shaders", "default.frag" ) )
        tex = self.resourcemanager.loadTexture2D( os.path.join(self.resource_dir, "textures", "uvmapping.png") )

        mesh.shaderMap = {'uv': 'in_text_coord_0', 'posiiton': 'in_position'}
        mat.textures = {0: tex}
        mat.texturesMap = {0: "texture_0"}
        
        
        mesh2 = self.resourcemanager.loadMesh( os.path.join(self.resource_dir, "models", "plane_Loc123_rot102030.fbx") )
        mesh.setMat(mat)
        mesh2.setMat(mat)

        ## 设置camera
        self.camera.setPosition((250, 250, 250))
        self.camera.setFOV(45)
        self.camera.setNearFarPlanes(0.1, 10000)
        self.camera.rotfromUE(225, -45, 0)


    def render(self, time: float, frametime: float):

        self.frameNumber += 1
        self.beforeRender()

        # Render cube to offscreen texture / fbo
        self.fbo.use()
        self.fbo.clear()

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0 ,0, 0)

        if self.camera:
            self.camera.tick()
            self.keyControlCamera(frametime)

        # 待渲染队列需要渲染
        for meshesInOneMatKey in self.renderLists:
            '''
            相同材质
            '''
            # TODO: 配置材质属性、包括镜头信息
            mat = self.renderListsMat[meshesInOneMatKey]
            mat.shader_program['view_matrix'].write(
                self.camera.view_matrix()
            )
            mat.shader_program['projection_matrix'].write(
                self.camera.projection_matrix()
            )
            # 分配每一个mesh的材质属性
            meshesInOneMat = self.renderLists[meshesInOneMatKey]
            for mesh in meshesInOneMat:
                mesh.tick()

        # Render UI to screen
        self.wnd.use()
        self.ui.render_ui()

        self.afterRender()


    def resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def keyControlCamera(self, frametime):
        velocity = self.SPEED * frametime
        if self.mouseRightPress == False:
            return
        if self.qweasd['W']:
            self.camera.moveForwardBackward(-velocity)
        elif self.qweasd['S']:
            self.camera.moveForwardBackward(velocity)
        if self.qweasd['A']:
            self.camera.moveLeftRight(velocity)
        elif self.qweasd['D']:
            self.camera.moveLeftRight(-velocity)
        if self.qweasd['Q']:
            self.camera.moveUpDown(velocity)
        elif self.qweasd['E']:
            self.camera.moveUpDown(-velocity)

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)
        # print('key_event, {}, {}, {}'.format(key, action, modifiers))
        if key == self.wnd.keys.W:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['W'] = True
            else:
                self.qweasd['W'] = False
        if key == self.wnd.keys.S:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['S'] = True
            else:
                self.qweasd['S'] = False
        if key == self.wnd.keys.A:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['A'] = True
            else:
                self.qweasd['A'] = False
        if key == self.wnd.keys.D:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['D'] = True
            else:
                self.qweasd['D'] = False
        if key == self.wnd.keys.Q:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['Q'] = True
            else:
                self.qweasd['Q'] = False
        if key == self.wnd.keys.E:
            if action == self.wnd.keys.ACTION_PRESS:
                self.qweasd['E'] = True
            else:
                self.qweasd['E'] = False

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

        # print('mouse_position_event, {}, {}, {}, {}'.format(x, y, dx, dy))

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        # print('mouse_drag_event, {}, {}, {}, {}'.format(x, y, dx, dy))
        if self.mouseRightPress:
            current_x = dx * self.SENSITIVITY
            current_y = dy * self.SENSITIVITY
            # ----> +x
            # |
            # v  +y
            # yaw此时绕世界坐标系旋转，而不是local的
            self.camera.yawGlobal(current_x)
            self.camera.pitch(current_y)


    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        # print('mouse_scroll_event, {}, {}'.format( x_offset, y_offset))

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)
        # print('mouse_press_event, {}, {}, {}'.format(x, y, button))
        if button == 1:
            self.mouseLeftPress = True
        elif button == 2:
            self.mouseRightPress = True


    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)
        # print('mouse_release_event, {}, {}, {}'.format(x, y, button))
        if button == 1:
            self.mouseLeftPress = False
        elif button == 2:
            self.mouseRightPress = False

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)

