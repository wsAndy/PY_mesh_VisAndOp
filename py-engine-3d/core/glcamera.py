
import glm
from .actor import Actor

class GLCamera(Actor):
    '''
    copy from https://github.com/tizian/Learning-OpenGL/blob/master/src/Camera.cpp

    此处相机坐标系完全按照opengl的坐标系，看向-Z，右侧 +X，上面 +Y
    # # yaw 从+y看-y，顺时针为正
    # # pitch 从+x看-x，顺时针为正
    # # roll 从+z看-z，顺时针为正
    #
    # yaw,pitch,roll = camera.cameraleftHand2RightHand(225, -45, 0)
    # camera.setYPR(yaw, pitch, roll)
    '''
    def __init__(self):
        super().__init__()
        self.m_position = glm.vec3(0,0,0)
        self.m_orientation = glm.fquat(1, 0, 0, 0)
        self.m_fov = 45
        self.m_nearPlane = 0.1
        self.m_farPlane = 100000
        self.aspect_ratio = 1.0


    def cameraleftHand2RightHand(self, yaw,pitch,roll):
        return yaw + 90, -pitch, roll

    def rotation(self):
        # 四元数转旋转，这么操作没问题，但是反过来不能直接 glm.quat_cast( rot_matrix )
        return glm.mat4_cast(self.m_orientation)
    def getPosition(self):
        return self.m_position
    def right(self):
        return glm.vec3(glm.row(self.rotation(),0))
    def up(self):
        return glm.vec3(glm.row(self.rotation(), 1))
    def forward(self):
        # 注意，相机是看向Z的负轴的，此处计算的foward实际是相机的背面
        return -glm.vec3(glm.row(self.rotation(), 2))
    def setPosition(self, position):
        self.m_position = glm.vec3(position)

    def move(self, delta):
        self.m_position += glm.vec3(delta)
    def moveLeftRight(self, delta: float):
        self.m_position -= delta * self.right()
    def moveUpDown(self, delta: float):
        self.m_position -= delta * self.up()
    def moveForwardBackward(self, delta: float):
        # 注意这边可能有bug
        self.m_position -= delta * self.forward()
    def rotate(self, angle, axis):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), axis))
        self.m_orientation *= rot
    def pitch(self, angle: float):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), self.right()))
        self.m_orientation *= rot
    def yaw(self, angle: float):
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), self.up()))
        self.m_orientation *= rot
    def roll(self, angle: float):
        # 为了保持镜头坐标系和opengl坐标系的旋转正负完全一致，此处的foward实际的背面,取angle也反一下
        rot = glm.normalize(glm.angleAxis( glm.radians(-angle), self.forward()))
        self.m_orientation *= rot

    def yawGlobal(self, angle: float):
        '''
        围绕世界的垂直方向转
        '''
        rot = glm.normalize(glm.angleAxis( glm.radians(angle), glm.vec3(0, 1, 0) ))
        self.m_orientation *= rot

    def rotfromUE(self, yaw:float, pitch:float, roll: float):
        '''
        设置从ue过来的旋转变量
        '''
        _yaw, _pitch, _roll = self.cameraleftHand2RightHand(yaw, pitch, roll)
        self.setYPR(_yaw, _pitch, _roll)

    def setYPR(self, yaw:float, pitch:float, roll: float):
        '''
        指定yaw、pitch、roll特定角度下的最终朝向
        '''
        oriQuat = glm.fquat(1, 0, 0, 0) 
        
        _up = glm.vec3(glm.row(glm.mat4_cast(oriQuat), 1))
        YawRot = glm.normalize(glm.angleAxis( glm.radians(yaw), _up))
        oriQuat *= YawRot

        _right = glm.vec3(glm.row(glm.mat4_cast(oriQuat), 0))
        PitchRot = glm.normalize(glm.angleAxis( glm.radians(pitch), _right ))
        oriQuat *= PitchRot
        
        _forward = -glm.vec3(glm.row(glm.mat4_cast(oriQuat), 2))
        RollRot = glm.normalize(glm.angleAxis( glm.radians(-roll), _forward))
        oriQuat *= RollRot

        self.m_orientation = oriQuat
        

    def resize(self, width, height):
        self.aspect_ratio = width / height

    def projection(self):
        return glm.perspective( glm.radians(self.m_fov), self.aspect_ratio, self.m_nearPlane, self.m_farPlane)
    def projection_matrix(self):
        return self.projection()

    def translation(self):
        return glm.translate(glm.mat4(), -self.m_position)
    def view(self):
        return self.rotation() * self.translation()
    def view_matrix(self):
        return self.view()
    def matrix(self):
        return self.projection() * self.view()
    def setFOV(self, fov_degree: float):
        # fov: degree
        self.m_fov = fov_degree
    def setNearFarPlanes(self, near, far):
        self.m_nearPlane = near
        self.m_farPlane = far

    def tick(self):
        super().tick()
        # print(self.rotation())
        # # self.yaw(-0.5)
        # print('------ camera ------')
        # print(self.getPosition())
        # print(self.forward())
        # print(self.up())
        # print(self.right())

        # self.pitch()
        pass

