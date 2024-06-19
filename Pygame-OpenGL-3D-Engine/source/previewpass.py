from .renderpassbase import RenderpassBase

class PreviewPass(RenderpassBase):

    def __init__(self):
        super().__init__()

    def tick(self, scene):
        [x.tick() for x in scene.models]
