

from core.scenemanager import SceneManager, run_window_config, create_parser
from core.resourcemanager import ResourceManager
import os
import platform
import sys


class App(SceneManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
            
        mesh = self.resourcemanager.loadMesh( path=os.path.join( ResourceManager.resource_dir, "models", "axes.fbx") )
        
        mat = self.resourcemanager.createCustomMaterial(vertex_path = os.path.join(ResourceManager.resource_dir, "shaders", "default.vert" ), fragment_path = os.path.join(ResourceManager.resource_dir, "shaders", "default.frag" ) )

        tex = self.resourcemanager.loadTexture2D( path=os.path.join(ResourceManager.resource_dir, "textures", "uvmapping.png") )

        mesh.shaderMap = {'uv': 'in_text_coord_0', 'posiiton': 'in_position'}
        mat.textures = {0: tex}
        mat.texturesMap = {0: "texture_0"}
        
        mesh2 = self.resourcemanager.loadMesh( os.path.join(ResourceManager.resource_dir, "models", "plane_Loc123_rot102030.fbx") )
        mesh.setMat(mat)
        mesh2.setMat(mat)



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
