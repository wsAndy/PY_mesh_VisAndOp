
class Scene:
    def __init__(self) -> None:
        self.models = []

    def add_model(self, model: any):
        self.models.append(model)

    def destroy(self, ):
        [x.destroy() for x in self.models]

    def render(self, ):
        [x.render() for x in self.models]