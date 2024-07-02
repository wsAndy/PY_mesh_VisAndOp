
from core.baserender import BaseRender

class ForwardRender(BaseRender):
    def __init__(self, scenemanager):
        super().__init__(scenemanager)
        pass

    def afterRender(self,):
        super().afterRender()

    def render(self,):
        super().render()
        # 待渲染队列需要渲染
        for meshesInOneMatKey in self.renderLists:
            '''
            相同材质
            '''
            # TODO: 配置材质属性、包括镜头信息
            mat = self.renderListsMat[meshesInOneMatKey]
            mat.shader_program['view_matrix'].write(
                self.sm.camera.view_matrix()
            )
            mat.shader_program['projection_matrix'].write(
                self.sm.camera.projection_matrix()
            )
            # 分配每一个mesh的材质属性
            meshesInOneMat = self.renderLists[meshesInOneMatKey]
            for mesh in meshesInOneMat:
                mesh.tick()

    def beforeRender(self,):
        super().beforeRender()