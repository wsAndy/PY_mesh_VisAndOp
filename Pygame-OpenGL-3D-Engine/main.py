from source.engine import Engine
import moderngl_window as mglw
from source.model import GlobalAxes
from source.model import CustomMesh
import os

class CustomApp(Engine):
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



if __name__ == "__main__":
    ## 可以把 run_window_config 放到外面来，也可以不放
    mglw.run_window_config(CustomApp)