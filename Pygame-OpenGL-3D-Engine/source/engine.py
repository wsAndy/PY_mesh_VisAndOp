import json
from typing import Any

from .scene import Scene
from source.actor import Actor

import moderngl
import pygame


class Engine:
    def __init__(self, window_size: tuple[int, int] = (800, 600), window_title: str = "ModernGL", gl_version: tuple[int, int] = (3, 3)):
        self.WINDOW_SIZE = window_size
        self.window_title = window_title
        self.gl_version = gl_version

        self.window = None

        # Initialize pygame
        pygame.init()
        pygame.display.set_caption(self.window_title)

        # Set OpenGL Attributes
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MAJOR_VERSION, self.gl_version[0])
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MINOR_VERSION, self.gl_version[1])
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

        # Create OpenGL Context
        self.window = pygame.display.set_mode(
            self.WINDOW_SIZE, pygame.OPENGL | pygame.DOUBLEBUF
        )

        # Mouse settings. 限制鼠标在窗口内
        # pygame.event.set_grab(True)
        # 隐藏鼠标
        # pygame.mouse.set_visible(False)

        # Create ModernGL Context
        self.ctx = moderngl.create_context()
        # Set the front face to clockwise
        # self.ctx.front_face = 'cw'
        # Enable depth test and face culling
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.time = 0.0
        self.delta_time = 0.0
        # Create a clock to limit the framerate
        self.clock = pygame.time.Clock()
        
        self.last_right_mouse = [0, 0]

    def set_camera(self, camera: Actor):
        self.camera = camera

    def set_scene(self, scene: Scene):
        # Scene
        self.scene = scene

    def get_time(self):
        self.time = pygame.time.get_ticks() / 1000.0

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.scene.destroy()
                pygame.quit()
                exit()

    def control_events(self):
        leftPick, midPick, rightPick =pygame.mouse.get_pressed()
        if rightPick != True:
            self.last_right_mouse = [0, 0]
            return
        SPEED = 1
        SENSITIVITY = 0.1

        # --------------- move 
        velocity = SPEED * self.delta_time
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.camera.moveForwardBackward(-velocity)
        if keys[pygame.K_s]:
            self.camera.moveForwardBackward(velocity)
        if keys[pygame.K_a]:
            self.camera.moveLeftRight(velocity)
        if keys[pygame.K_d]:
            self.camera.moveLeftRight(-velocity)
        if keys[pygame.K_q]:
            self.camera.moveUpDown(velocity)
        if keys[pygame.K_e]:
            self.camera.moveUpDown(-velocity)

        # --------------- rotate 
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if abs(self.last_right_mouse[0]) < 1 or abs(self.last_right_mouse[1]) < 1:
            self.last_right_mouse = [mouse_x, mouse_y]
            return

        current_x = (mouse_x - self.last_right_mouse[0] ) * SENSITIVITY
        current_y = (mouse_y - self.last_right_mouse[1] ) * SENSITIVITY

        self.last_right_mouse = [mouse_x, mouse_y]

        self.camera.yaw(current_x)
        self.camera.pitch(current_y)


    def tick(self):
        # Clear the framebuffer
        # self.ctx.clear(0.08, 0.16, 0.16)
        self.ctx.clear(0, 0, 0)

        # Render the scene
        self.scene.tick()

        # Swap the buffers
        pygame.display.flip()

    def run(self):
        # Print OpenGL Version
        # print(json.dumps(self.ctx.info, indent=2))

        while True:  
            self.get_time()
            self.check_events()
            self.control_events()
            self.camera.tick()
            self.tick()
            self.delta_time = self.clock.tick(60)
