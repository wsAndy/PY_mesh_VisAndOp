
class RendererBase:

    renderpass = []
    models = []
    textures = []
    def __init__(self) -> None:
        pass

    def add_pass(self, rpass):
        '''
        添加render pass
        '''
        self.renderpass.append(rpass)

    def add_model(self, model: any):
        self.models.append(model)

    def add_tex(self, tex: any):
        self.textures.append(tex)

    def destroy(self, ):
        self.renderpass = []
        [x.destroy() for x in self.models]
        [x.destory() for x in self.textures]

    def tick(self, ):
        [x.tick(self) for x in self.renderpass ]
        # [x.tick() for x in self.models]