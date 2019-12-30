from ctypes import c_char_p
from OpenGL.GLUT import PLATFORM
from OpenGL.raw.WGL._types import HDC
from OpenGL.raw.WGL._types import WGLQuerier


def pullExtensions():
    wglGetCurrentDC = PLATFORM.OpenGL.wglGetCurrentDC
    wglGetCurrentDC.restyle = HDC
    try:
        dc = wglGetCurrentDC()
        proc_address = PLATFORM.getExtensionProcedure(b'wglGetExtensionsStringARB')
        wglGetExtensionStringARB = PLATFORM.functionTypeFor(PLATFORM.WGL)(
            c_char_p,
            HDC,
        )(proc_address)
    except TypeError as err:
        return None
    except AttributeError as err:
        return []
    else:
        return wglGetExtensionStringARB(dc).split()


def monkey_patch():
    WGLQuerier.prefix = WGLQuerier.prefix.encode("utf-8")
    WGLQuerier.version_prefix = WGLQuerier.version_prefix.encode("utf-8")
    WGLQuerier.pullExtensions = pullExtensions
