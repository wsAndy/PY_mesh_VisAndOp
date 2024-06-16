from source.engine import Engine
import moderngl_window as mglw
from source.model import GlobalAxes
from source.model import CustomMesh
import os

from PIL import Image
class CustomApp(Engine):

    rtWindowWidth = 1280
    rtWindowHeight = 720
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setCamera()
        self.setMesh()

    def setCamera(self):
        self.camera.setPosition((250, 250, 250))
        self.camera.setFOV(45)
        self.camera.setNearFarPlanes(0.1, 10000)
        yaw, pitch, roll = self.camera.cameraleftHand2RightHand(225, -45, 0)
        self.camera.setYPR(yaw, pitch, roll)

    def setMesh(self):
        model2 = CustomMesh(self)
        model2.loadModel(os.path.join(self.resource_dir, r"models/axes.fbx"))
        self.scene.add_model(model2)

        globalAxes = GlobalAxes(self)
        self.scene.add_model(globalAxes)

    def key_event(self, key, action, modifiers):
        super().key_event(key, action, modifiers)

        if key == self.wnd.keys.NUMBER_1 and action == self.wnd.keys.ACTION_PRESS:
            # self.wnd.fbo 就把整个编辑器截图了
            image = Image.frombytes('RGBA', self.wnd.fbo.size, self.wnd.fbo.read(components=4))
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save('editor.png', format='png')
            print('save image')
        if key == self.wnd.keys.NUMBER_2 and action == self.wnd.keys.ACTION_PRESS:
            # self.wnd.fbo 就把整个编辑器截图了
            image = Image.frombytes('RGBA', self.fbo.size, self.fbo.read(components=4))
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image.save('rt.png', format='png')
            print('save image')


if __name__ == "__main__":
    ## 对于有需要外部指定部分参数的情况，可以把 run_window_config 放到外面来，控制输入到 CustomApp的比那辆
    mglw.run_window_config(CustomApp)