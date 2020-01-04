from pygame import Color
from pygame.rect import Rect

from opengl_support.font import Font

START_VIEW_TITLE = "Sokoban"
START_VIEW_START = "Start"
START_VIEW_OPTIONS = "Options"
START_VIEW_HELP = "Help"
START_VIEW_QUIT = "Quit"

OPTIONS_VIEW_CONTROLS = "Controls"
OPTIONS_VIEW_SOUND = "Sound"
OPTIONS_VIEW_GRAPHICS = "Graphics"
OPTIONS_VIEW_BACK = "Back"

# Map view
MAP_VIEW_YOU_WIN = "You Win!"


def draw_text_with_border(font: Font, text_to_draw: str, color: Color, rect: Rect, border_colour: Color,
                          border_width: float):
    """
    Draw text on the screen with a border
    :param font: the font to use
    :param text_to_draw: the text to draw
    :param color: the colour to use for the main font
    :param rect: the rectangle to draw in
    :param border_colour: the colour of the border
    :param border_width: the width of the border
    :return: nothing
    """
    font.draw_text(text_to_draw, border_colour, rect.move(border_width, 0))
    font.draw_text(text_to_draw, border_colour, rect.move(border_width, border_width))
    font.draw_text(text_to_draw, border_colour, rect.move(border_width, -border_width))
    font.draw_text(text_to_draw, border_colour, rect.move(0, 0))
    font.draw_text(text_to_draw, border_colour, rect.move(0, border_width))
    font.draw_text(text_to_draw, border_colour, rect.move(0, -border_width))
    font.draw_text(text_to_draw, border_colour, rect.move(-border_width, 0))
    font.draw_text(text_to_draw, border_colour, rect.move(-border_width, border_width))
    font.draw_text(text_to_draw, border_colour, rect.move(-border_width, -border_width))
    font.draw_text(text_to_draw, color, rect)
