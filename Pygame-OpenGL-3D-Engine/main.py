from source.glcamera import GLCamera
from source.engine import Engine
from source.model import Cube
from source.model import Triangle
from source.model import CustomMesh
from source.scene import Scene
import os

if __name__ == "__main__":
    engine = Engine(gl_version=(4, 6),window_size=(512, 512))

    camera = GLCamera(engine)
    camera.setPosition((250, 250, 250))
    camera.setFOV(45)
    camera.setNearFarPlanes(0.1, 10000)

    # yaw 从+y看-y，顺时针为正
    # pitch 从+x看-x，顺时针为正
    # roll 从+z看-z，顺时针为正

    yaw,pitch,roll = camera.cameraleftHand2RightHand(225, -45, 30)
    camera.setYPR(yaw, pitch, roll)

    engine.set_camera(camera)

    # model = CustomMesh(engine)
    # model.loadModel( os.path.join(r"./assets/models/plane.fbx") )

    model2 = CustomMesh(engine)
    model2.loadModel( os.path.join(r"./assets/models/axes.fbx") )

    yaw,pitch,roll=model2.leftHand2RightHand(10, 20, 30)
    model2.transformComponent.setYPR(yaw, pitch, roll)
    

    scene = Scene()
    # scene.add_model(model)
    scene.add_model(model2)
    # scene.add_model(triangle)
    
    engine.set_scene(scene)
    engine.run()
