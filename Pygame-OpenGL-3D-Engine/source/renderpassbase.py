
from pathlib import Path

class RenderpassBase:
    resource_dir = (Path(__file__).parent / '../assets').resolve()
    shader_dir = (Path(__file__).parent / '../source/shaders').resolve()
    def __init__(self):
        pass

    def tick(self, scene):
        pass

