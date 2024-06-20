

from core.scenemanager import SceneManager
import os
import argparse
import sys
import moderngl_window as mglw




if __name__ == "__main__":
    ## 对于有需要外部指定部分参数的情况，可以把 run_window_config 放到外面来，控制输入到 CustomApp的比那辆
    ## 入参控制也可以参考：https://github.com/moderngl/moderngl-window/blob/master/examples/modify_parser.py

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-width",
        "--width",
        type=int,
        default=1920,
        help="renderer width",
        required=False,
    )
    parser.add_argument(
        "-height",
        "--height",
        type=int,
        default=1080,
        help="renderer height",
        required=False,
    )
    values = parser.parse_args(sys.argv[1:])

    ## 不走offscreen
    mglw.run_window_config(config_cls=SceneManager )

    # ## 走offscreen
    # if platform.system().lower() == 'windows':
    #     mglw.run_window_config(config_cls=CustomApp, args=("--window", "headless") )
    # elif platform.system().lower() == 'linux':
    #     mglw.run_window_config(config_cls=CustomApp, args=("--window", "headless", "--backend", "egl") )