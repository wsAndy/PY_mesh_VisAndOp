import json
from typing import Any

import moderngl_window as mglw
import imgui
from moderngl_window import geometry
from moderngl_window.integrations.imgui import ModernglWindowRenderer

from pathlib import Path
import moderngl
from .glcamera import GLCamera
from .scene import Scene
from .model import CustomMesh
from .model import GlobalAxes
import os

class Engine(mglw.WindowConfig):
    gl_version = (4, 6)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent / '../assets').resolve()
    shader_dir = (Path(__file__).parent / '../source/shaders').resolve()


    SPEED = 1000
    SENSITIVITY = 0.1

    aspect_ratio = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()

        self.imgui = ModernglWindowRenderer(self.wnd)

        self.camera = GLCamera(self)
        self.camera.setPosition((250, 250, 250))
        self.camera.setFOV(45)
        self.camera.setNearFarPlanes(0.1, 10000)
        yaw, pitch, roll = self.camera.cameraleftHand2RightHand(225, -45, 0)
        self.camera.setYPR(yaw, pitch, roll)

        self.scene = Scene()

        model2 = CustomMesh(self)
        model2.loadModel(os.path.join(self.resource_dir, r"models/axes.fbx"))
        self.scene.add_model(model2)

        globalAxes = GlobalAxes(self)
        self.scene.add_model(globalAxes)

        self.mouseLeftPress = False
        self.mouseRightPress = False
        self.qweasd = {'Q': False, 'W': False, 'E':False, 'A':False, 'S':False, 'D': False }

    def setCamera(self, cam):
        self.camera = cam
    def setScene(self, scene):
        self.scene = scene

    def render(self, time: float, frametime: float):

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0 ,0, 0)

        if self.camera:
            self.camera.tick()
            self.keyControlCamera(frametime)

        if self.scene:
            self.scene.tick()

        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.show_test_window()

        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored("Eggs", 0.2, 1., 0.)
        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())


    def resize(self, width: int, height: int):
        self.camera.resize(width, height)
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


# class Engine(mglw.WindowConfig):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self.gl_version = (3, 3)
#         self.title = "imgui Integration"
#         self.aspect_ratio = 1
#         self.resizable = True
#         self.samples = 8
#
#         imgui.create_context()
#         self.wnd.ctx.error
#         self.imgui = ModernglWindowRenderer(self.wnd)
#
#
#         # self.resource_dir = (Path(__file__).parent / 'resources').resolve()
#         aspect_ratio = None
#         #
#         # self.WINDOW_SIZE = window_size
#         # self.window_title = window_title
#         # self.gl_version = gl_version
#         self.resource_dir = (Path(__file__) / '../assets').resolve()
#
#         self.window = None
#
#         # # Initialize pygame
#         # pygame.init()
#         # pygame.display.set_caption(self.window_title)
#         #
#         # # Set OpenGL Attributes
#         # pygame.display.gl_set_attribute(
#         #     pygame.GL_CONTEXT_MAJOR_VERSION, self.gl_version[0])
#         # pygame.display.gl_set_attribute(
#         #     pygame.GL_CONTEXT_MINOR_VERSION, self.gl_version[1])
#         # pygame.display.gl_set_attribute(
#         #     pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
#
#         # # Create OpenGL Context
#         # self.window = pygame.display.set_mode(
#         #     self.WINDOW_SIZE, pygame.OPENGL | pygame.DOUBLEBUF
#         # )
#
#         # Mouse settings. 限制鼠标在窗口内
#         # pygame.event.set_grab(True)
#         # 隐藏鼠标
#         # pygame.mouse.set_visible(False)
#
#         # Create ModernGL Context
#         self.ctx = moderngl.create_context()
#         # Set the front face to clockwise
#         # self.ctx.front_face = 'cw'
#         # Enable depth test and face culling
#         self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
#
#         self.time = 0.0
#         self.delta_time = 0.0
#         # Create a clock to limit the framerate
#         self.clock = pygame.time.Clock()
#
#         self.last_right_mouse = [0, 0]
#
#     def set_camera(self, camera):
#         self.camera = camera
#
#     def set_scene(self, scene):
#         # Scene
#         self.scene = scene
#
#     def get_time(self):
#         self.time = pygame.time.get_ticks() / 1000.0
#
#     def check_events(self):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
#                 self.scene.destroy()
#                 pygame.quit()
#                 exit()
#
#     def control_events(self):
#         '''
#         镜头控制
#         '''
#         leftPick, midPick, rightPick =pygame.mouse.get_pressed()
#
#         if rightPick != True:
#             self.last_right_mouse = [0, 0]
#             return
#
#         SPEED = 1
#         SENSITIVITY = 0.1
#
#         # --------------- rotate
#         mouse_x, mouse_y = pygame.mouse.get_pos()
#         if abs(self.last_right_mouse[0]) < 1 or abs(self.last_right_mouse[1]) < 1:
#             self.last_right_mouse = [mouse_x, mouse_y]
#             return
#         current_x = (mouse_x - self.last_right_mouse[0] ) * SENSITIVITY
#         current_y = (mouse_y - self.last_right_mouse[1] ) * SENSITIVITY
#         # ----> +x
#         # |
#         # v  +y
#         self.last_right_mouse = [mouse_x, mouse_y]
#         # yaw此时绕世界坐标系旋转，而不是local的
#         self.camera.yawGlobal(current_x)
#         self.camera.pitch(current_y)
#
#         # # --------------- move
#         velocity = SPEED * self.delta_time
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_w]:
#             self.camera.moveForwardBackward(-velocity)
#         if keys[pygame.K_s]:
#             self.camera.moveForwardBackward(velocity)
#         if keys[pygame.K_a]:
#             self.camera.moveLeftRight(velocity)
#         if keys[pygame.K_d]:
#             self.camera.moveLeftRight(-velocity)
#         if keys[pygame.K_q]:
#             self.camera.moveUpDown(velocity)
#         if keys[pygame.K_e]:
#             self.camera.moveUpDown(-velocity)
#
#
#     def tick(self):
#         # Clear the framebuffer
#         # self.ctx.clear(0.08, 0.16, 0.16)
#         self.ctx.clear(0, 0, 0)
#
#         # Render the scene
#         self.scene.tick()
#
#         # Swap the buffers
#         pygame.display.flip()
#
#     def run(self):
#         # Print OpenGL Version
#         # print(json.dumps(self.ctx.info, indent=2))
#
#         while True:
#             self.get_time()
#             self.check_events()
#             self.control_events()
#             self.camera.tick()
#             self.tick()
#             self.delta_time = self.clock.tick(60)
