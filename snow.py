import numpy as np
import pygame
import noise
import random
from pygame.locals import *

MAX_SNOW_FLAKE_SIZE = 5
MIN_SNOW_FLAKE_SIZE = 1
GRAVITY = 0.000001


class SnowFlake():

    def __init__(self, width, height,
                 surface_fill,
                 initial_position=None,
                 initial_velocity=None):
        # Index 0 = width, index 1 = height
        self.screen_details = (width, height)

        """
        Index 0 is the x value, index 1 is the y value and
        the index 2 is the z axis,
        also the snow flake distance from the screen
        and its apparent size
        """
        if (initial_position is not None and initial_velocity is not None):
            self.position = np.array(initial_position, dtype=float)
            self.rate_of_change = np.array(initial_velocity, dtype=float)
        else:
            self.randomize()

        self.previous_position = self.position.copy()
        """
        The snow flake is a square surface
        with the same size as the flake's z distance
        """
        apparent_size = int(self.position[2])
        self.snow_flake_skin = pygame.Surface((apparent_size, apparent_size))
        self.snow_flake_skin.fill((255, 255, 255))

        """
        The same surface as the snow flake skin
        but with the color of the background
        """
        self.snow_flake_patch = pygame.Surface((apparent_size, apparent_size))
        self.snow_flake_patch.fill(tuple(surface_fill)[0:3])

    def contained(self):
        """
        Check if the flake is within the screen
        """
        x = self.position[0]
        y = self.position[1]
        width = self.screen_details[0]
        height = self.screen_details[1]
        if ((x >= 0 and x <= width) and (y >= 0 and y <= height)):
            return True
        else:
            return False

    def wind(self, vx, vy, vz=0):
        # Damp the movement based on the size
        vy /= self.position[2]
        vx /= self.position[2]
        # Add the 'wind force'
        self.rate_of_change += np.array([vx, vy, vz], dtype=float)

    def randomize(self, perlin_x=None, perlin_y=None):
        """
        Uses perlin noise to generate
        starting positions (only X's and Z's)
        and starting velocities
        """
        width = self.screen_details[0]
        height = self.screen_details[1]
        if (perlin_x is None and perlin_y is None):
            random.seed()
            perlin_x = random.random()
            perlin_y = random.random()
        flake_initial_x = random.randint(0, width - 10)
        flake_initial_y = 0.0
        flake_initial_z = random.randint(MIN_SNOW_FLAKE_SIZE,
                                         MAX_SNOW_FLAKE_SIZE)
        self.position = np.array([flake_initial_x,
                                  flake_initial_y,
                                  flake_initial_z])
        flake_initial_vx = 0.0
        flake_initial_vy = (noise.pnoise2(perlin_x, perlin_y) + 0.5)
        flake_initial_vy *= flake_initial_z
        flake_initial_vz = 0.0
        self.rate_of_change = np.array([flake_initial_vx,
                                        flake_initial_vy,
                                        flake_initial_vz])

    def update_position(self):
        """
        Check if the flake is contained
        within the screen. If it is,
        update it's current position
        and resize the particle.
        In case it's offscreen, redraw it
        at the top of the screen
        """
        if (self.contained()):
            self.previous_position = self.position.copy()
            self.rate_of_change[1] += GRAVITY
            self.position += self.rate_of_change
            apparent_size = int(self.position[2])
            previous_apparent_size = int(self.previous_position[2])
            if (previous_apparent_size != apparent_size):
                apparent_square_size = (apparent_size, apparent_size)
                self.snow_flake_skin = pygame.transform \
                                             .smoothscale(self.snow_flake_skin,
                                                          apparent_square_size)
        else:
            self.randomize()

    def draw(self, surface):
        """
        Get the current x and y position
        and draw the snow skin at that location
        """
        x_y_position = (int(self.position[0]), int(self.position[1]))
        surface.blit(self.snow_flake_skin, x_y_position)

    def undraw(self, surface):
        """
        Get the current x and y position
        and undraw the snow at that location.
        Actually draws a surface with the same colour
        as the background
        """
        x_y_position = (int(self.position[0]), int(self.position[1]))
        surface.blit(self.snow_flake_patch, x_y_position)
