

from core.scenemanager import SceneManager, run_window_config, create_parser
from core.resourcemanager import ResourceManager
from core.geometry.globalaxes import GlobalAxes
import os
import platform
import sys
from core.ui import UI

import imgui
class CustomUI(UI):
    '''
    自定义ui 执行逻辑
    '''
    def __init__(self, manager):
        super().__init__(manager)
    def customLogic(self):
        import random
        #### button example
        with imgui.begin("Example: Change Material"):
            btn_mat = imgui.button('Mat1')
            with imgui.begin_drag_drop_source() as drag_drop_src:
                if drag_drop_src.dragging:
                    imgui.set_drag_drop_payload('itemtype', b'payload')
                    imgui.button('dragged source')
            if btn_mat:
                # 如果是编辑器，就需要做选中状态判断
                # 这边简单一些，直接把指定名字的模型的材质改掉, 在目前所有材质中随便取一个
                matIdList = [ x for x in range(len(self.sm.resourcemanager.materials)) ]
                for mesh in self.sm.resourcemanager.meshes:
                    if mesh.label == "big1":
                        mesh.setMat( self.sm.resourcemanager.materials[ random.choice(matIdList)] )


class App(SceneManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
            
        mesh = self.resourcemanager.loadMesh( path=os.path.join( ResourceManager.resource_dir, "models", "axes.fbx") )
        mesh.label = "big1"
        # for mat1:  default
        mesh.shaderMap = {'uv': 'in_text_coord_0', 'posiiton': 'in_position'}
        
        ###################
        mat = self.resourcemanager.createCustomMaterial(vertex_path = os.path.join(ResourceManager.resource_dir, "shaders", "default.vert" ), fragment_path = os.path.join(ResourceManager.resource_dir, "shaders", "default.frag" ) )

        tex = self.resourcemanager.loadTexture2D( path=os.path.join(ResourceManager.resource_dir, "textures", "uvmapping.png") )
        ## mat中有texture的情况，需要指定使用哪个location对应哪个texture数据，以及location在glsl中对应哪个变量
        mat.textures = {0: tex}
        mat.texturesMap = {0: "texture_0"}
        #################################

        ## 指定material为 basecolor
        mat2 = self.resourcemanager.createCustomMaterial(glslpath=os.path.join(ResourceManager.resource_dir, "shaders", "basecolor.glsl" ))
        # 对于basecolor的情况，需要指定basecolor
        mat2.setBaseColor([0.1, 0.5, 1])
        
        
        mesh2 = self.resourcemanager.loadMesh( os.path.join(ResourceManager.resource_dir, "models", "plane_Loc123_rot102030.fbx") )

        ## 分别指定不同的材质
        mesh.setMat(mat2)
        mesh2.setMat(mat)

        # 绘制坐标轴
        GlobalAxes(self)

        ## 自定义ui
        self.ui = CustomUI(self)
        

if __name__ == "__main__":

    parser = create_parser()
    parser.add_argument(
        "-offscreen",
        "--offscreen",
        default=False,
        const=True,
        action='store_const',
        help="hidden window or not",
        required=False,
    )

    values = parser.parse_args(sys.argv[1:])
    
    if values.offscreen:
        ## 走offscreen
        if platform.system().lower() == 'windows':
            run_window_config(config_cls=App, parser=parser, args=("--window", "headless") )
        elif platform.system().lower() == 'linux':
            run_window_config(config_cls=App, parser=parser, args=("--window", "headless", "--backend", "egl") )
    else:
        ## 不走offscreen
        run_window_config(config_cls=App, parser=parser)
