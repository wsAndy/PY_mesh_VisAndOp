from source.freecamera import FreeCamera
from source.engine import Engine
from source.model import Cube
from source.model import Triangle
from source.model import CustomMesh
from source.scene import Scene
import os

if __name__ == "__main__":
    engine = Engine(gl_version=(4, 6))
    engine.set_camera(FreeCamera(engine, (250, 250, 250)))

    # model = CustomMesh(engine)
    # model.loadModel( os.path.join(r"./assets/models/plane.fbx") )

    model2 = CustomMesh(engine)
    model2.loadModel( os.path.join(r"./assets/models/axes.fbx") )

    triangle = Triangle(engine)

    scene = Scene()
    # scene.add_model(model)
    # scene.add_model(model2)
    scene.add_model(triangle)
    
    engine.set_scene(scene)
    engine.run()
