import glm
import pygame
import numpy as np
from source.actor import Actor
from source.engine import Engine

import trimesh

FOV = 45.0
NEAR = 0.1
FAR = 10000.0
SPEED = 1 #0.01
SENSITIVITY = 0.1


class FreeCamera(Actor):
    def __init__(self, app: Engine, position=(5.0, 5.0, 5.0) ):
        super().__init__()
        self.app = app
        self.aspect_ratio = app.WINDOW_SIZE[0] / app.WINDOW_SIZE[1]
        # Projection Matrix
        self.projection_matrix = self.get_projection_matrix()
        self.last_right_mouse = [0, 0]

        self.initRTS(position)

    @property
    def location(self, ):
        return self.transformComponent.location
    @location.setter
    def location(self, loc):
        self.transformComponent.location = loc
        
    @property
    def yaw(self, ):
        return self.transformComponent.yaw
    @yaw.setter
    def yaw(self, yaw):
        self.transformComponent.yaw = yaw
        
    @property
    def pitch(self, ):
        return self.transformComponent.pitch
    @pitch.setter
    def pitch(self, pitch):
        self.transformComponent.pitch = pitch

    @property
    def roll(self, ):
        return self.transformComponent.roll
    @roll.setter
    def roll(self, roll):
        self.transformComponent.roll = roll

    def initRTS(self, position):

        # Camera Position
        self.location = position
        
        # View Matrix (eye, center, up)
        self.view_matrix = glm.lookAt(
            self.location, 
            glm.vec3(0.0, 0.0, 0.0), 
            glm.vec3(0.0, 1.0, 0.0)
        )

        self.viewMatrix2RightUpForward()

    def viewMatrix2RightUpForward(self, ):

        inverted = np.array( glm.inverse(self.view_matrix).to_list())
        # 按照行排列
        # right,    X
        # up        Y
        # -forward  Z
        ## Right Vector
        # self.right = glm.vec3( inverted[0][0], inverted[0][1], inverted[0][2])
        ## Up Vector
        # self.up = glm.vec3( inverted[1][0], inverted[1][1], inverted[1][2])
        ## Forward Vector
        # self.forward = glm.vec3( -inverted[2][0], -inverted[2][1], -inverted[2][2])

        # 简化表达
        self.right = glm.vec3( glm.row(inverted, 0).xyz )
        self.up = glm.vec3( glm.row(inverted, 1).xyz )
        self.forward = glm.vec3( -glm.row(inverted, 2).xyz )
        
        # 只用旋转的部分(0：3，0：3)
        rot_mat = glm.quat_cast( self.view_matrix)
        yaw, pitch, roll = glm.eulerAngles(rot_mat)
        
        # Yaw and Pitch
        self.yaw = glm.degrees(yaw)
        self.pitch = glm.degrees(pitch)
        self.roll = glm.degrees(roll)


    def fromUE( self, location, rotation ):
        def ueypr2opengl(yaw, pitch,roll):
            return 270 - yaw, pitch, -roll
        def ueloc2opengl(x,y,z):
            return x, z, y
        x,y,z = ueloc2opengl(location[0], location[1], location[2])
        yaw, pitch, roll = ueypr2opengl(rotation[0], rotation[1], rotation[2])
        
        # rotmat = trimesh.transformations.euler_matrix( glm.radians(roll), glm.radians(pitch), glm.radians(yaw), 'szxy')

        quad = glm.quat( glm.radians(glm.vec3(yaw,roll,pitch)))
        rotation = glm.mat4_cast(quad)

        return rotation
        # 这边还有明显的问题，暂时没有对齐

        pass
    def toUE( self, ):
        pass
    def fromBlender( self, location, rotation ):
        self.location = np.matmul( np.array(location),np.array([ [1, 0, 0], [0, 0, 1], [0, -1, 0]]) )
        
    def toBlender( self,):
        loc = np.matmul( self.location, np.array([ [1, 0, 0], [0, 0, -1], [0, 1, 0]]) )
        pass

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)

    def move(self):
        leftPick, midPick, rightPick =pygame.mouse.get_pressed()
        if rightPick != True:
            return
        
        velocity = SPEED * self.app.delta_time
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.location += self.forward * velocity
        if keys[pygame.K_s]:
            self.location -= self.forward * velocity
        if keys[pygame.K_a]:
            self.location -= self.right * velocity
        if keys[pygame.K_d]:
            self.location += self.right * velocity
        if keys[pygame.K_q]:
            self.location -= self.up * velocity
        if keys[pygame.K_e]:
            self.location += self.up * velocity


    def _rotate(self, ):

        if self.pitch > 89.9:
            self.pitch = 89.9
        if self.pitch < -89.9:
            self.pitch = -89.9

        forward = glm.vec3(0,0,0)
        right = glm.vec3(0,0,0)
        up = glm.vec3(0,0,0)
        # Update camera vectors
        forward.x = -glm.cos( glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        forward.y = glm.sin(glm.radians(self.pitch))
        forward.z = -glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        forward = glm.normalize(forward)

        right = glm.normalize(
            glm.cross(forward, glm.vec3(0.0, 1.0, 0.0)))
        up = glm.normalize(glm.cross(right, forward))

        # print("================")
        # print("{}, {}".format(self.yaw, self.pitch ))
        # print(forward)
        # print(right)
        # print(up)

        self.forward = forward
        self.right = right
        self.up = up

    def rotate(self):
        leftPick, midPick, rightPick =pygame.mouse.get_pressed()
        '''
        1 - left click
        2 - middle click
        3 - right click
        4 - scroll up
        5 - scroll down
        '''
        if rightPick != True:
            self.last_right_mouse = [0, 0]
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if abs(self.last_right_mouse[0]) < 1 or abs(self.last_right_mouse[1]) < 1:
            self.last_right_mouse = [mouse_x, mouse_y]
            return

        current_x = (mouse_x - self.last_right_mouse[0] ) * SENSITIVITY
        current_y = (mouse_y - self.last_right_mouse[1] ) * SENSITIVITY

        self.last_right_mouse = [mouse_x, mouse_y]
        
        self.yaw += current_x
        self.pitch -= current_y

        self._rotate()


    def tick(self):
        super().tick()
        
        self.move()
        self.rotate()

        # print('========++++======')
        # print( self.forward )
        # print( self.right )
        # print( self.up )

        # rot_matrix = self.fromUE([0,0,0],[ 10, 20, 30 ] )

        self.view_matrix = glm.lookAt(
            self.location, self.location + self.forward, self.up
        )

        print( "yaw = {:.2f}, pitch = {:.2f}, roll = {:.2f}".format( self.yaw, self.pitch, self.roll) )

        # 打印之后，发现这个数据不对，居然还有roll，显然上述camera的计算过程中有bug

        # for i in range(3):
        #     for j in range(3):
        #         self.view_matrix[i][j] = rot_matrix[i][j]
        
        # print("====================")
        # print(self.view_matrix)

        



