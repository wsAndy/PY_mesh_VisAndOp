import moderngl_window as mglw
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer

from pathlib import Path
import moderngl
from .glcamera import GLCamera
from .rendererbase import RendererBase

class Engine(mglw.WindowConfig):
    gl_version = (4, 6)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent / '../assets').resolve()
    shader_dir = (Path(__file__).parent / '../source/shaders').resolve()

    SPEED = 1000
    SENSITIVITY = 0.1

    frameNumber = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()

        self.imgui = ModernglWindowRenderer(self.wnd)
        self.camera = GLCamera()
        self.activeRenderer = None

        if self.rtWindowWidth is None:
            self.rtWindowWidth = 512
        if self.rtWindowHeight is None:
            self.rtWindowHeight = 512

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((self.rtWindowWidth, self.rtWindowHeight), 4),
            depth_attachment=self.ctx.depth_texture((self.rtWindowWidth, self.rtWindowHeight)),
        )
        self.camera.resize(self.rtWindowWidth, self.rtWindowHeight)
        # Ensure imgui knows about this texture
        # This is the color layer in the framebuffer
        self.imgui.register_texture(self.fbo.color_attachments[0])

        self.mouseLeftPress = False
        self.mouseRightPress = False
        self.qweasd = {'Q': False, 'W': False, 'E':False, 'A':False, 'S':False, 'D': False }

    def updateRenderer(self, renderer):
        self.activeRenderer = renderer

    def render(self, time: float, frametime: float):
        # Render cube to offscreen texture / fbo
        self.fbo.use()
        self.fbo.clear()

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0 ,0, 0)

        if self.camera:
            self.camera.tick()
            self.keyControlCamera(frametime)

        if self.activeRenderer:
            self.activeRenderer.tick()

        # Render UI to screen
        self.wnd.use()
        self.render_ui()

        self.frameNumber += 1

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

        # Create window with the framebuffer image
        imgui.begin("Custom window with Image", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_SCROLL_WITH_MOUSE)
        # Create an image control by passing in the OpenGL texture ID (glo)
        # and pass in the image size as well.
        # The texture needs to he registered using register_texture for this to work
        imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size, (0, 1), (1, 0) )
        imgui.end()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())


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

