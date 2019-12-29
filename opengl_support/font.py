from collections import deque
from typing import Optional, Tuple, Dict

import pygame
from OpenGL.GL import glGenTextures, glTexImage2D, GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, \
    glTexParameterf, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE, \
    glTexEnvi, glLoadIdentity, glBindTexture, \
    glBegin, GL_QUADS, glTexCoord2f, glVertex3i, glEnd, GL_NEAREST, GL_LINEAR
from pygame.rect import Rect

DEFAULT_MAX_FONT_CACHE_SIZE = 100


class Font:
    """
    A font that can be rendered to the screen with OpenGL.

    This works by rendering a pygame font to a surface, and then loading it into an OpenGL
    texture. This takes CPU processing, so to reduce the impact the font will cache
    the rendered data in memory (but still the program's memory).

    The cache stores combinations of text and colour for the font, so resizing does not increase
    the cache.

    Caching can be disabled or enabled. The cache will not grow beyond a fixed number of combinations
    as passed in the constructor. After this, the first value added is popped in a FIFO order.
    """
    def __init__(self, font: pygame.font.Font, max_cache_size: int = DEFAULT_MAX_FONT_CACHE_SIZE):
        self.__texture_id = glGenTextures(1)
        self.__font: pygame.font.FontType = font

        # Cache is from text colour combination to surface, image data
        self.__cache: Dict[Tuple[str, Tuple], Tuple[pygame.SurfaceType, str]] = dict()
        self.__cache_queue: deque = deque()
        self.__cache_enabled = True
        self.__max_cache_size: int = max_cache_size

        self.__previous_texture_bound: Optional[Tuple[str, Tuple]] = None

    def disable_cache(self):
        """
        Disable the caching of this font. This prevents the font remembering what it can to
        reduce CPU processing.
        """
        self.__cache_enabled = False

    def enable_cache(self):
        """
        Turn on caching so this font remembers as much as it can from CPU processing.
        """
        self.__cache_enabled = True

    def empty_cache(self):
        """
        Empty this font's cache.
        """
        self.__cache.clear()
        self.__cache_queue.clear()

    @property
    def is_cache_enabled(self) -> bool:
        return self.__cache_enabled

    def reload(self):
        """
        Resets the font's cache. This is required if the screen size changes for example.
        """
        self.empty_cache()
        self.__previous_texture_bound = None

    def draw_text(self, text: str, font_colour: pygame.Color, rect: Rect):
        """
        Draw the given text with the given colour in the provided rectangle.
        This uses the original font provided when this object was created.
        The cache is used if possible and enabled.
        :param text: the text to draw
        :param font_colour: the colour of the text
        :param rect: where to draw the text. It will be stretched to fill the area
        :return: nothing
        """
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
        """
        Load a font so it can be drawn. Unlike other methods, this actually binds the specific text and font
        colour to the texture in GPU memory. This utilises the CPU cache if enabled.
        :param text: the text to render
        :param font_colour: the colour of the font
        :return: nothing
        """
        if self.__previous_texture_bound == (text, font_colour):
            return

        if self.is_cache_enabled:
            self.update_cache(text, font_colour)
            surface, texture_data = self.__cache[text, tuple(font_colour)]
        else:
            surface = self.__render_font(text, font_colour)
            texture_data = self.__convert_to_image_data(surface)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        self.__previous_texture_bound = text, font_colour

    def get_surface(self, text: str, font_colour: pygame.Color) -> pygame.SurfaceType:
        """
        Get the rendered surface for a particular font. Uses the cache if possible
        :param text: the text to render
        :param font_colour: the colour to apply
        :return: the rendered surface
        """
        if self.is_cache_enabled:
            self.update_cache(text, font_colour)
            return self.__cache[text, tuple(font_colour)][0]

        return self.__render_font(text, font_colour)

    def update_cache(self, text: str, colour: pygame.Color):
        """
        Update the cache with a given text and font colour combination
        :param text: the text that will be written
        :param colour: the colour of the text that will be written
        :return: nothing
        """
        if not self.is_cache_enabled:
            return

        if (text, tuple(colour)) in self.__cache:
            return

        if len(self.__cache_queue) >= self.__max_cache_size:
            index = self.__cache_queue.popleft()
            self.__cache.pop(index, None)

        self.__cache_queue.append((text, tuple(colour)))
        surface = self.__render_font(text, colour)
        data = self.__convert_to_image_data(surface)
        self.__cache[text, tuple(colour)] = surface, data

    def __render_font(self, text: str, colour: pygame.Color) -> pygame.SurfaceType:
        return self.__font.render(text, True, colour)

    @staticmethod
    def __convert_to_image_data(surface: pygame.SurfaceType) -> str:
        return pygame.image.tostring(surface, "RGBA", False)

    @property
    def texture_id(self):
        return self.__texture_id
