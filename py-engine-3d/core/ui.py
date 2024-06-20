
import imgui

class UI:

    def __init__(self, manager) -> None:
        imgui.create_context()
        self.sm = manager

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
        imgui.image(self.sm.fbo.color_attachments[0].glo, *self.sm.fbo.size, (0, 1), (1, 0) )
        imgui.end()

        imgui.render()
        self.sm.imgui.render(imgui.get_draw_data())