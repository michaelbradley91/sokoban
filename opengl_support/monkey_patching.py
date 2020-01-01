from ctypes import c_char_p
from OpenGL.GLUT import PLATFORM
# noinspection PyProtectedMember
from OpenGL.raw.WGL._types import HDC
# noinspection PyProtectedMember
from OpenGL.raw.WGL._types import WGLQuerier


def pull_extensions():
    wgl_get_current_dc = PLATFORM.OpenGL.wglGetCurrentDC
    wgl_get_current_dc.restyle = HDC
    try:
        dc = wgl_get_current_dc()
        process_address = PLATFORM.getExtensionProcedure(b'wglGetExtensionsStringARB')
        wgl_extension_string_arb = PLATFORM.functionTypeFor(PLATFORM.WGL)(
            c_char_p,
            HDC,
        )(process_address)
    except TypeError:
        return None
    except AttributeError:
        return []
    else:
        return wgl_extension_string_arb(dc).split()


def monkey_patch():
    WGLQuerier.prefix = WGLQuerier.prefix.encode("utf-8")
    WGLQuerier.version_prefix = WGLQuerier.version_prefix.encode("utf-8")
    WGLQuerier.pullExtensions = pull_extensions
