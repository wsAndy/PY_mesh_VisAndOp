
import os
from core.resourcemanager import ResourceManager, DrawMode

class GlobalAxes:
    def __init__(self, manager):
    
        mat2 = manager.resourcemanager.createCustomMaterial(glslpath= os.path.join(ResourceManager.resource_dir, "shaders", "basecolor.glsl"))

        globalAxesX = manager.resourcemanager.createLine((0,0,0), (10000, 0,0))
        globalAxesX.drawmode = DrawMode.LINES
        globalAxesX.basecolor = (1, 0, 0)

        globalAxesY = manager.resourcemanager.createLine((0,0,0), (0, 10000,0))
        globalAxesY.drawmode = DrawMode.LINES
        globalAxesY.basecolor = (0, 1, 0)

        globalAxesZ = manager.resourcemanager.createLine((0,0,0), (0, 0, 10000))
        globalAxesZ.drawmode = DrawMode.LINES
        globalAxesZ.basecolor = (0, 0, 1)

        globalAxesX.setMat(mat2)
        globalAxesY.setMat(mat2)
        globalAxesZ.setMat(mat2)
