import pygame
from typing import Tuple

from OpenGL.GL import *
from pygame.surface import SurfaceType


DEFAULT_BACKGROUND_COLOUR = pygame.Color("black")


def load_texture_to_surface(path: str) -> SurfaceType:
    """
    Load the given path into a PyGame surface.
    :param path:  the path to load
    :return: a PyGame surface suitable for a texture
    """
    return pygame.image.load(path)


def init_opengl(display: SurfaceType):
    """
    Enable Open GL for the given display. May be called more than once.
    :param display: the display
    :return: nothing
    """

    # Enable required features
    glEnable(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glEnable(GL_BLEND)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Orthogonal projection for 2d coordinates
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, display.get_width(), display.get_height(), 0, 0, 1)
    glMatrixMode(GL_MODELVIEW)

    set_background_and_clear(DEFAULT_BACKGROUND_COLOUR)


def set_background_and_clear(colour: pygame.Color):
    """
    Set the background colour and clear the canvas, effectively filling it with that colour.
    :param colour: the background colour
    :return: nothing
    """
    glClearColor(colour.r / 255, colour.g / 255, colour.b / 255, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
