import glm

from source.components.baseComponent import BaseComponent

class TransformComponent(BaseComponent):

    def __init__(self, x = 0, y = 0, z = 0) -> None:
        super().__init__()
        self._location = glm.vec3(x,y,z)

        # # 内部变量都用弧度表达
        # self._yaw = glm.radians(yaw)
        # self._pitch = glm.radians(pitch)
        # self._roll = glm.radians(roll)
        self._scale = glm.vec3(1,1,1)
        self._m_orientation = glm.fquat(1, 0, 0, 0)
    
    def right(self):
        return glm.vec3(glm.row(self.rotation(), 0))
    def up(self):
        return glm.vec3(glm.row(self.rotation(), 1))
    def forward(self):
        return -glm.vec3(glm.row(self.rotation(), 2))
    
    def rotate(self, angle, axis):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), axis))
        self._m_orientation *= rot
    def pitch(self, angle: float):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), self.right()))
        self._m_orientation *= rot
    def yaw(self, angle: float):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), self.up()))
        self._m_orientation *= rot
    def roll(self, angle: float):
        rot = glm.normalize(glm.angleAxis( glm.radians(-angle), self.forward()))
        self._m_orientation *= rot


    # @property
    def rotation(self,):
        return glm.mat4_cast(self._m_orientation)
    # @rotation.setter
    # def rotation(self, xyz):
    #     if isinstance(xyz, list) or isinstance(xyz, tuple):
    #         self._m_orientation = glm.fquat(xyz)
    #     elif isinstance(xyz, glm.fquat):
    #         self._m_orientation = xyz

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

    # @property
    # def yaw(self,):
    #     return glm.degrees(self._yaw)
    # @yaw.setter
    # def yaw(self, x):
    #     self._yaw = glm.radians(x)

    # @property
    # def pitch(self,):
    #     return glm.degrees(self._pitch)
    # @pitch.setter
    # def pitch(self, x):
    #     self._pitch = glm.radians(x)

    # @property
    # def roll(self,):
    #     return glm.degrees(self._roll)
    # @roll.setter
    # def roll(self, x):
    #     self._roll = glm.radians(x)

    def destroy(self,):
        super().destroy()
        self.location = glm.vec3(0,0,0)
        # self.yaw = 0
        # self.pitch = 0
        # self.roll = 0
        self.scale = glm.vec3(1,1,1)
        self._m_orientation = glm.fquat(1, 0, 0, 0)
    
