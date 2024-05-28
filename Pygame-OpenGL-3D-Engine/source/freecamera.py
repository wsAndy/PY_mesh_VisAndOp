import glm
import pygame
import numpy as np

from source.engine import Engine

FOV = 45.0
NEAR = 0.1
FAR = 100.0
SPEED = 0.01
SENSITIVITY = 0.05


class FreeCamera:
    def __init__(self, app: Engine, position=(5.0, 5.0, 5.0) ):
        self.app = app
        self.aspect_ratio = app.WINDOW_SIZE[0] / app.WINDOW_SIZE[1]

        # Camera Position
        self.position = glm.vec3(position)


        # View Matrix (eye, center, up)
        self.view_matrix = glm.lookAt(
            self.position, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0)
        )

        inverted = np.array( glm.inverse(self.view_matrix).to_list())
        # 按照行排列
        # right, 
        # up
        # -forward
        # Right Vector
        self.right = glm.vec3( inverted[0][0], inverted[0][1], inverted[0][2])
        # Up Vector
        self.up = glm.vec3( inverted[1][0], inverted[1][1], inverted[1][2])
        # Forward Vector
        self.forward = glm.vec3( -inverted[2][0], -inverted[2][1], -inverted[2][2])
        

        # 只用旋转的部分(0：3，0：3)
        rot_mat = glm.quat_cast( self.view_matrix)
        yaw, pitch, roll = glm.eulerAngles(rot_mat)
        
        # Yaw and Pitch
        self.yaw = glm.degrees(yaw)
        self.pitch = glm.degrees(pitch)
        self.roll = glm.degrees(roll)

        # Projection Matrix
        self.projection_matrix = self.get_projection_matrix()

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)

    def move(self):
        velocity = SPEED * self.app.delta_time
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.position += self.forward * velocity
        if keys[pygame.K_s]:
            self.position -= self.forward * velocity
        if keys[pygame.K_a]:
            self.position -= self.right * velocity
        if keys[pygame.K_d]:
            self.position += self.right * velocity
        if keys[pygame.K_q]:
            self.position -= self.up * velocity
        if keys[pygame.K_e]:
            self.position += self.up * velocity

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_rel()
        mouse_x *= SENSITIVITY
        mouse_y *= SENSITIVITY

        self.yaw += mouse_x
        self.pitch -= mouse_y

        if self.pitch > 89.9:
            self.pitch = 89.9
        if self.pitch < -89.9:
            self.pitch = -89.9

        forward = glm.vec3(0,0,0)
        right = glm.vec3(0,0,0)
        up = glm.vec3(0,0,0)
        # Update camera vectors
        forward.x = -glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
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

    def update(self):
        self.move()
        self.rotate()

        # print('========++++======')
        # print( self.forward )
        # print( self.right )
        # print( self.up )

        self.view_matrix = glm.lookAt(
            self.position, self.position + self.forward, self.up
        )



