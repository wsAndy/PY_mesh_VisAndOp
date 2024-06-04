import glm

from source.components.baseComponent import BaseComponent

class TransformComponent(BaseComponent):

    def __init__(self, x = 0, y = 0, z = 0, yaw = 0, pitch = 0, roll = 0) -> None:
        super().__init__()
        self._location = glm.vec3(x,y,z)

        # 内部变量都用弧度表达
        self._yaw = glm.radians(yaw)
        self._pitch = glm.radians(pitch)
        self._roll = glm.radians(roll)
        self._scale = glm.vec3(1,1,1)

    @property
    def location(self,):
        return self._location
    @location.setter
    def location(self, xyz):
        if isinstance(xyz, list) or isinstance(xyz, tuple):
            self._location = glm.vec3(xyz)
        elif isinstance(xyz, glm.vec3):
            self._location = xyz
        else:
            self._location = glm.vec3(xyz, xyz, xyz)

    @property
    def scale(self,):
        return self._scale
    @scale.setter
    def scale(self, xyz):
        if isinstance(xyz, list):
            self._scale = glm.vec3(xyz)
        elif isinstance(xyz, glm.vec3):
            self._scale = xyz
        else:
            self._scale = glm.vec3(xyz, xyz, xyz)

    @property
    def yaw(self,):
        return glm.degrees(self._yaw)
    @yaw.setter
    def yaw(self, x):
        self._yaw = glm.radians(x)

    @property
    def pitch(self,):
        return glm.degrees(self._pitch)
    @pitch.setter
    def pitch(self, x):
        self._pitch = glm.radians(x)

    @property
    def roll(self,):
        return glm.degrees(self._roll)
    @roll.setter
    def roll(self, x):
        self._roll = glm.radians(x)

    def destroy(self,):
        super().destroy()
        self.location = glm.vec3(0,0,0)
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.scale = glm.vec3(1,1,1)
    
