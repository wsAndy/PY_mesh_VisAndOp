
'''
场景中的所有物体都是一个Actor
Actor可以挂载 component
'''

from .components.baseComponent import BaseComponent
from .components.transformComp import TransformComponent

class Actor:
    transformComponent: TransformComponent
    def __init__(self) -> None:
        self.transformComponent = TransformComponent()
        
        self.components: list[BaseComponent] = [self.transformComponent]
    
    def tick(self, ):
        [x.tick() for x in self.components]

    def destroy(self, ):

        [x.destroy() for x in self.components]

    

