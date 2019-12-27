from typing import Optional

import pygame
from OpenGL.GL import glGenTextures, glTexImage2D, GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, \
    glTexParameterf, GL_TEXTURE_WRAP_S, GL_REPEAT, GL_TEXTURE_WRAP_T, GL_TEXTURE_MAG_FILTER, GL_LINEAR, \
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE, glTexEnvi, glLoadIdentity, glBindTexture, \
    glBegin, GL_QUADS, glTexCoord2f, glVertex3i, glEnd, GL_NEAREST
from pygame.rect import Rect


class Font:
    def __init__(self, font: pygame.font.Font):
        self.__texture_id = glGenTextures(1)
        self.__font: pygame.font.FontType = font
        self.__font_surface: Optional[pygame.SurfaceType] = None
        self.__previous_text: Optional[str] = None
        self.__previous_colour: Optional[pygame.Color] = None
        self.__previous_texture_set: bool = False

    def reload(self):
        self.__font_surface = None
        self.__previous_text = None
        self.__previous_colour = None
        self.__previous_texture_set = False

    def get_surface(self, text: str, font_colour: pygame.Color) -> pygame.SurfaceType:
        if self.__previous_text == text and self.__previous_colour == font_colour:
            return self.__font_surface

        self.__previous_texture_set = False
        self.__previous_text = text
        self.__previous_colour = font_colour
        self.__font_surface: pygame.SurfaceType = self.__font.render(text, True, font_colour)

        return self.__font_surface

    def draw_text(self, text: str, font_colour: pygame.Color, rect: Rect):
        self.load_font(text, font_colour)
        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3i(rect.x, rect.y, 0)
        glTexCoord2f(1, 0)
        glVertex3i(rect.right, rect.y, 0)
        glTexCoord2f(1, 1)
        glVertex3i(rect.right, rect.bottom, 0)
        glTexCoord2f(0, 1)
        glVertex3i(rect.x, rect.bottom, 0)
        glEnd()

    def load_font(self, text: str, font_colour: pygame.Color):
        if self.__previous_text != text or self.__previous_colour != font_colour:
            self.get_surface(text, font_colour)

        if self.__previous_texture_set:
            return

        texture_data = pygame.image.tostring(self.__font_surface, "RGBA", False)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__font_surface.get_width(), self.__font_surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        self.__previous_texture_set = True

    @property
    def texture_id(self):
        return self.__texture_id
