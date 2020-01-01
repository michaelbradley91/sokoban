import pygame
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, glLoadIdentity, GL_CLAMP_TO_EDGE, glTexParameteri, \
    glEnable, GL_BLEND, \
    GL_COLOR_MATERIAL, GL_MULTISAMPLE, GL_SAMPLE_ALPHA_TO_COVERAGE, GL_SRC_ALPHA, glBlendFunc, GL_ONE_MINUS_SRC_ALPHA, \
    glBlendFuncSeparate, glClearColor, GL_ONE, GL_PROJECTION, glMatrixMode, glOrtho, GL_MODELVIEW, GL_COLOR_BUFFER_BIT, \
    GL_DEPTH_BUFFER_BIT, glClear
from pygame.surface import SurfaceType
# noinspection PyBroadException
try:
    import OpenGL.raw.WGL.EXT.swap_control as wgl_swap_control
except BaseException:
    pass
# noinspection PyBroadException
try:
    import OpenGL.raw.GLX.EXT.swap_control as glx_swap_control
except BaseException:
    pass

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


# noinspection PyBroadException
def try_enable_vsync() -> bool:
    """
    Tries to enable vsync.
    Note that the refresh rate is hard to get, so it is easier to just start
    measuring it manually and throttle if needed.
    :return: True if vsync might be enabled, and false otherwise.
    """
    # In case platforms support unexpected extensions, just try everything and
    # catch errors if they occur...
    try:
        glx_swap_control.glXSwapIntervalEXT(True)
        return True
    except BaseException:
        pass

    try:
        wgl_swap_control.wglSwapIntervalEXT(True)
        return True
    except BaseException:
        pass

    return False
