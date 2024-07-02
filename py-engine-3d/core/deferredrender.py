
from core.baserender import BaseRender
import os

class DeferredRender(BaseRender):
    def __init__(self, scenemanager):
        super().__init__(scenemanager)

        self.g_view_z = self.sm.ctx.texture(self.sm.wnd.buffer_size, 1, dtype="f2")
        self.g_normal = self.sm.ctx.texture(self.sm.wnd.buffer_size, 3, dtype="f2")
        self.g_depth = self.sm.ctx.depth_texture(self.sm.wnd.buffer_size)
        self.g_buffer = self.sm.ctx.framebuffer(
            color_attachments=[self.g_view_z, self.g_normal],
            depth_attachment=self.g_depth
        )

        # Load the geometry program.
        self.geometry_program = self.sm.load_program( os.path.join(self.inside_shader_dir, "geometry.glsl") )
        # # Load the shading program.
        # self.shading_program = self.sm.load_program( os.path.join(self.inside_shader_dir, "debug.glsl"))
        # self.shading_program["g_view_z"].value = 0
        # self.shading_program["g_normal"].value = 1
        # self.shading_program["ssao_occlusion"].value = 2

    def afterRender(self,):
         super().afterRender()

    def render(self,):
        super().render()
        self.g_buffer.clear(0.0, 0.0, 0.0)
        self.g_buffer.use()

        # 待渲染队列需要渲染 GBuffer
        for meshesInOneMatKey in self.renderLists:

            self.geometry_program['view_matrix'].write(
                self.sm.camera.view_matrix()
            )
            self.geometry_program['projection_matrix'].write(
                self.sm.camera.projection_matrix()
            )
            ## 正常来说，mesh使用的材质就使用了geometry_program的内容吧
            # mat = self.renderListsMat[meshesInOneMatKey]
            # mat.shader_program['view_matrix'].write(
            #     self.sm.camera.view_matrix()
            # )
            # mat.shader_program['projection_matrix'].write(
            #     self.sm.camera.projection_matrix()
            # )
            # 分配每一个mesh的材质属性
            meshesInOneMat = self.renderLists[meshesInOneMatKey]
            for mesh in meshesInOneMat:
                mesh.tick()
                # 这边不断把内容draw到 g_buffer 中，然后最后再统一针对gbuffer做渲染


        # 然后再加上灯光
        ##

    def beforeRender(self,):
        super().beforeRender()