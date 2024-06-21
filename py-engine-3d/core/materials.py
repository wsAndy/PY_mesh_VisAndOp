import uuid
import numpy as np
import moderngl
import moderngl_window

class BaseMaterial:
    shader_program: moderngl.Program = None
    textures = {} # {0: moderngl.texture, 1:xxx}
    texturesMap = {} # {0: "texture_0", 1: "xxx"}

    _basecolor = None

    @property
    def ctx(self):
        """moderngl.Context: The current context"""
        return moderngl_window.ctx()
    
    def setBaseColor(self, color):
        if len(color) == 3:
            self._basecolor = np.array(color).astype('f4').tobytes()

    def updateModelMatrix(self, model_matrix):
        self.shader_program['model_matrix'].write(model_matrix)

    def updateTexture(self, ):
        for texId in self.textures:
            _shaderTexName = self.texturesMap[texId]
            self.textures[texId].use(location= texId)
            self.shader_program[_shaderTexName] = texId

    def updateBaseColor(self, color = None):
        if "base_color" in self.shader_program :
            if color is not None:
                self.shader_program['base_color'].write( np.array(color).astype('f4').tobytes() )
            elif self._basecolor:
                self.shader_program['base_color'].write(self._basecolor)
            

    def isReady(self, ):
        if self.shader_program:
            return True
        return False
    
    def __init__(self) -> None:
        self.id = str(uuid.uuid4())

class CustomMaterial(BaseMaterial):
    def __init__(self, shader) -> None:
        super().__init__()
        self.shader_program = shader


class PBRMaterial(BaseMaterial):
    def __init__(self) -> None:
        super().__init__()
        pass    