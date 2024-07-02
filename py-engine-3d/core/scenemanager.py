'''
主入口，持有
resourcemanager
tick
UI
'''
import moderngl_window as mglw


from .ui import UI
import moderngl
from .glcamera import GLCamera
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.context.base import WindowConfig
from moderngl_window import geometry
from .resourcemanager import ResourceManager

from .forwardrender import ForwardRender
from .deferredrender import DeferredRender
from enum import Enum
class ERenderingMode(Enum):
    Forward = 1
    Deferred = 2

def create_parser():
    parser = mglw.create_parser()

    parser.add_argument(
        "-width",
        "--width",
        type=int,
        default=512,
        help="renderer width",
        required=False,
    )
    parser.add_argument(
        "-height",
        "--height",
        type=int,
        default=512,
        help="renderer height",
        required=False,
    )

    return parser

def run_window_config(config_cls: WindowConfig, parser, timer=None, args=None, ) -> None:
    """
    Run an WindowConfig entering a blocking main loop

    Args:
        config_cls: The WindowConfig class to render
    Keyword Args:
        timer: A custom timer instance
        args: Override sys.args
    """
    mglw.setup_basic_logging(config_cls.log_level)
    # parser = mglw.create_parser()
    config_cls.add_arguments(parser)
    values = mglw.parse_args(args=args, parser=parser)
    config_cls.argv = values
    window_cls = mglw.get_local_window_cls(values.window)

    # Calculate window size
    size = values.size or config_cls.window_size
    size = int(size[0] * values.size_mult), int(size[1] * values.size_mult)

    # Resolve cursor
    show_cursor = values.cursor
    if show_cursor is None:
        show_cursor = config_cls.cursor

    window = window_cls(
        title=config_cls.title,
        size=size,
        fullscreen=config_cls.fullscreen or values.fullscreen,
        resizable=values.resizable
        if values.resizable is not None
        else config_cls.resizable,
        visible=config_cls.visible,
        gl_version=config_cls.gl_version,
        aspect_ratio=config_cls.aspect_ratio,
        vsync=values.vsync if values.vsync is not None else config_cls.vsync,
        samples=values.samples if values.samples is not None else config_cls.samples,
        cursor=show_cursor if show_cursor is not None else True,
        backend=values.backend,
    )
    window.print_context_info()
    mglw.activate_context(window=window)
    timer = timer or mglw.Timer()
    config = config_cls(ctx=window.ctx, wnd=window, timer=timer)
    # Avoid the event assigning in the property setter for now
    # We want the even assigning to happen in WindowConfig.__init__
    # so users are free to assign them in their own __init__.
    window._config = mglw.weakref.ref(config)

    # Swap buffers once before staring the main loop.
    # This can trigged additional resize events reporting
    # a more accurate buffer size
    window.swap_buffers()
    window.set_default_viewport()

    timer.start()

    while not window.is_closing:
        current_time, delta = timer.next_frame()

        if config.clear_color is not None:
            window.clear(*config.clear_color)

        # Always bind the window framebuffer before calling render
        window.use()

        window.render(current_time, delta)
        if not window.is_closing:
            window.swap_buffers()

    _, duration = timer.stop()
    window.destroy()
    if duration > 0:
        mglw.logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )


class SceneManager(mglw.WindowConfig):
    gl_version = (4, 6)
    customInfo = {}
    title = "imgui Integration"

    SPEED = 1000
    SENSITIVITY = 0.1

    frameNumber = 0
    rtWindowWidth = 512
    rtWindowHeight = 512

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = UI(self)

        self.rtWindowWidth = self.argv.width
        self.rtWindowHeight = self.argv.height

        self.camera = GLCamera()
        self.resourcemanager = ResourceManager(self)

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

        ## 设置camera
        self.camera.setPosition((250, 250, 250))
        self.camera.setFOV(45)
        self.camera.setNearFarPlanes(0.1, 10000)
        self.camera.rotfromUE(225, -45, 0)

        self.afterInit()

    def afterInit(self, ):
        '''
        默认走forward管线
        '''
        self.changeRenderMode(ERenderingMode.Forward)

    def changeRenderMode(self, mode: ERenderingMode):
        self.renderMode = mode
        if mode is ERenderingMode.Forward:
            self.renderer = ForwardRender(self)
        elif mode is ERenderingMode.Deferred:
            self.renderer = DeferredRender(self)

    def render(self, time: float, frametime: float):

        self.frameNumber += 1
        self.renderer.beforeRender()

        # Render cube to offscreen texture / fbo
        self.fbo.use()
        self.fbo.clear()

        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0 ,0, 0)

        if self.camera:
            self.camera.tick()
            self.keyControlCamera(frametime)

        self.renderer.render()

        # Render UI to screen
        self.wnd.use()
        self.ui.render_ui()

        self.renderer.afterRender()


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

