import sys
import os
import utils_ws as ut
from loguru import logger
import open3d as o3d
import numpy as np
import time
import mitsuba as mi

from mesh_meshlab2mitsuba import getMitsubaMesh


isDebug = True if sys.gettrace() else False

def getModel():
    model_name = os.path.join(r"D:\assets\suzanne.obj")
    model = o3d.io.read_triangle_mesh(model_name)
    material = o3d.visualization.rendering.MaterialRecord()
    material.shader = "defaultLit"
    # albedo_name = "albedo.jpeg"
    # material.albedo_img = o3d.io.read_image(albedo_name)
    return (model, material)

if __name__ == '__main__':
    ut.initLog()

    logger.info("================================")

    ## EGL Headless is not supported on this platform.
    render = o3d.visualization.rendering.OffscreenRenderer(640, 480)
    model, mat=getModel()
    render.scene.set_background([0, 0, 0, 0])
    render.scene.add_geometry("model", model, mat)
    render.scene.set_lighting(render.scene.LightingProfile.NO_SHADOWS, (0, 0, 0))
    render.scene.camera.look_at([2.47, -2.46, 2.5], [0, 0, 0],  [-0.45, 0.43, 0.78])
    img_o3d = render.render_to_image()
    o3d.io.write_image("mtest2.jpeg", img_o3d, 9)

    ## get camera parameter by GUI
    # render = o3d.visualization.Visualizer()
    # render.create_window()
    # model, mat = getModel()
    # render.add_geometry(model)
    # render.run()
    ### load camera parameter from json file( 从GUI中按下p键得到 )
    # parameters = o3d.io.read_pinhole_camera_parameters("ScreenCamera_<somedate>.json")
    # render.setup_camera(parameters.intrinsic, parameters.extrinsic)

