from source.freecamera import FreeCamera
from source.engine import Engine
from source.model import Cube
from source.model import CustomMesh
import os

if __name__ == "__main__":
    engine = Engine(gl_version=(4, 6))
    engine.set_camera(FreeCamera(engine))

    model = CustomMesh(engine)
    model.loadModel( os.path.join(r"C:\Users\admin\Documents\cube.fbx") )
    # model = Cube(engine)
    engine.set_scene(model)
    engine.run()
