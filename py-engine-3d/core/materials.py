import uuid


class BaseMaterial:
    shader_program = None
    textures = {} # {0: moderngl.texture, 1:xxx}
    texturesMap = {} # {0: "texture_0", 1: "xxx"}

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