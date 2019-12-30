from typing import Optional

import pygame
from OpenGL.GL import glGenTextures, glBindTexture, glTexImage2D, GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, \
    glTexParameterf, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE, \
    glTexEnvi, glLoadIdentity, glBegin, \
    GL_QUADS, glTexCoord2f, glVertex3i, glEnd, GL_NEAREST, glVertex3f
from pygame.rect import Rect

from opengl_support.drawable import Drawable


class Texture(Drawable):
    """
    An OpenGL texture. This should be reloaded whenever the window changes size.
    """
    def __init__(self, surface: pygame.SurfaceType):
        """
        Initialise the texture with the given PyGame surface.
        :param surface: the surface to load

        Note: fonts rendered to surfaces can be passed in here as well. Generally making them large
        is the simplest way to ensure they look good.
        """
        self.__texture_id = glGenTextures(1)
        self.__surface: pygame.SurfaceType = surface
        self.__texture_data = pygame.image.tostring(self.__surface, "RGBA", False)

    def reload(self):
        """
        Reload the texture, as required when the window changes size.
        :return: nothing
        """
        glBindTexture(GL_TEXTURE_2D, self.__texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__surface.get_width(), self.__surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.__texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    def draw_sub_rectangle(self, rect: Rect, sub_rectangle: Optional[Rect] = None):
        """
        Draw this texture in the given rect. If provided, only draws the sub_rectangle of the texture
        in the target rectangle.
        :param rect: the rectangle to draw in
        :param sub_rectangle: the portion of the texture to draw in that rectangle
        :return: nothing
        """
        if not sub_rectangle:
            sub_rectangle = self.__surface.get_rect()

        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(sub_rectangle.x / self.width, sub_rectangle.y / self.height)
        glVertex3f(rect.x, rect.y, 0)
        glTexCoord2f(sub_rectangle.right / self.width, sub_rectangle.y / self.height)
        glVertex3f(rect.right, rect.y, 0)
        glTexCoord2f(sub_rectangle.right / self.width, sub_rectangle.bottom / self.height)
        glVertex3f(rect.right, rect.bottom, 0)
        glTexCoord2f(sub_rectangle.x / self.width, sub_rectangle.bottom / self.height)
        glVertex3f(rect.x, rect.bottom, 0)
        glEnd()

    def draw(self, rect: Rect):
        self.draw_sub_rectangle(rect)

    @property
    def surface(self):
        return self.__surface

    @property
    def texture_id(self):
        return self.__texture_id

    @property
    def width(self):
        return self.__surface.get_width()

    @property
    def height(self):
        return self.__surface.get_height()

    @property
    def size(self):
        return self.__surface.get_size()
