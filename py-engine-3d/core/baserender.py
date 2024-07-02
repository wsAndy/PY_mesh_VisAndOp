
from pathlib import Path

class BaseRender:
    inside_shader_dir = (Path(__file__).parent / 'inside-shader').resolve()

    # 当前次渲染队列
    renderLists = {} # key: material.id, values: list[Mesh]
    renderListsMat = {} # key: material.id, values: material

    def __init__(self, scenemanager):
        self.sm = scenemanager
        pass

    def render(self,):
        pass

    # 渲染前做资源分配
    def beforeRender(self,):
        '''
        检查下，如果 renderLists没有变化，则不需要重新装配
        否则，需要装配
        '''
        if self.sm.resourcemanager.isChanged():
            self.renderLists = {}
            self.renderListsMat = {}
            '''
            重新做装配
            '''
            for mesh in self.sm.resourcemanager.meshes:
                # 根据材质id做分配
                matId = mesh.getMatId()
                if matId in self.renderLists:
                    self.renderLists[matId].append(mesh)
                else:
                    self.renderLists[matId] = [mesh]
                # 根据材质id做分配
                if matId not in self.renderListsMat:
                    self.renderListsMat[matId] = mesh.getMat()

    def afterRender(self,):
        self.sm.resourcemanager.changed = False
