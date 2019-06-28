import pygame
import numpy as np
import random
import sys
import math
import noise
from snow import *

SNOW_FLAKES_QUANTITY = 200


class main():
    _continue_flag = True

    def __init__(self, width, height):
        pygame.init()
        """
        If any of the dimensions is zero
        enable fullscreen mode
        """
        if (width == 0 or height == 0):
            self.canvas = pygame.display \
                                .set_mode(
                                         (width, height),
                                          pygame.NOFRAME |
                                          pygame.FULLSCREEN)
        else:
            self.canvas = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Snow Flake Fall")
        self.canvas.fill((0, 0, 0))
        # Sets the width and height
        screen_details = pygame.display.Info()
        self.width = screen_details.current_w
        self.height = screen_details.current_h

        # Pre-create the mouse array
        self.mouse = np.zeros(2)
        self.mouse_down = False

        # Some constants
        self.inverse_square_width = 1 / self.width ** 2
        self.inverse_square_height = 1 / self.height ** 2
        self.inverse_square_screen = np.array(
                                              [self.inverse_square_width,
                                               self.inverse_square_height])

    def start(self):
        """
        Since numpy arrays aren`t dinamic,
        first append the flakes to a list,
        then make an array out of that list
        """
        flakes = []
        for i in range(0, SNOW_FLAKES_QUANTITY):
            flakes.append(SnowFlake(self.width, self.height, self.canvas.get_at((0, 0))))
        self.snow_flakes = np.array(flakes)

        # Get a clock object
        self.clock = pygame.time.Clock()


    def apply_wind(self, flake):
        # Get the diff for each aaxis
        x_y_diff = flake.position[0:2] - self.mouse
        # Normalize the diff, but with squared values
        x_y_diff *= self.inverse_square_screen
        # Apply this formulae to each axis: (val - src) * -1 + dst
        x_y_diff[0] = (x_y_diff[0] + 1 if (x_y_diff[0] < 0) else 0) \
            * -1 + 0 if (x_y_diff[0] < 0) else 1
        x_y_diff[1] = (x_y_diff[1] + 1 if (x_y_diff[1] < 0) else 0) \
            * -1 + 0 if (x_y_diff[1] < 0) else 1
        # Apply a bit of dampening
        x_y_diff *= 0.05
        # Then apply the 'wind' force into the flake
        x_diff = x_y_diff[0]
        y_diff = x_y_diff[1]
        flake.wind(x_diff, y_diff)

    def flake_routine(self, angle, flake):
        if (self.mouse.all(0)):
            """
            Only apply the wind,
            if the mouse is within the screen
            and has a button hold down
            """
            self.apply_wind(flake)
        # Apply continuos 'random' winds
        flake.wind(angle * 0.05, 0, 0)
        # Drawing sequence
        flake.undraw(self.canvas)
        flake.update_position()
        flake.draw(self.canvas)

    def loop(self):
        """
        First create some local variables
        for the perlin noise
        """
        x_offset = 0
        perlin_x = 0
        perlin_y = 0
        while self._continue_flag is True:
            # Calculates the x 'swing'
            x_offset = noise.pnoise2(perlin_x, perlin_y)
            perlin_x += 0.01
            perlin_y += 0.01
            # Apply the usual routine to each flake
            for flake in self.snow_flakes:
                self.flake_routine(x_offset, flake)
            # Update the entire screen
            pygame.display.update()
            # Lock the frame rate at 60 fps
            self.clock.tick(60)
            # Handles the events
            for event in pygame.event.get():
                # Quit the program if the use close the windows
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    self._continue_flag = False
                # Or press ESCAPE
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        self._continue_flag = False 
                """
                Only will get the current mouse x and y
                for the wind if a button is down
                """ 
                if (event.type == pygame.MOUSEBUTTONDOWN):
                    self.mouse_down = True
                    self.mouse[:] = event.pos

                elif (event.type == pygame.MOUSEMOTION and
                        self.mouse_down is True):
                    if (math.isfinite(event.pos[0]) and
                            math.isfinite(event.pos[1])):
                        self.mouse[:] = event.pos

                elif (event.type == pygame.MOUSEBUTTONUP):
                    self.mouse_down = False
                    self.mouse.fill(0)


m = main(0, 0)
m.start()
m.loop()
