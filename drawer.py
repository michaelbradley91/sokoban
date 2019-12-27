import pygame

from pygame.rect import Rect

from direction import Direction
from opengl_support.helpers import set_background_and_clear
from resources import Resources


class Drawer:
    """
    A class for drawing things
    """
    def __init__(self, resources: Resources):
        self.__resources = resources

    def draw_you_win(self, text: str, colour: pygame.Color, rect: Rect):
        self.__resources.you_win_font.draw_text(text, colour, rect)

    def draw_crate(self, rect: Rect):
        self.__resources.tiles1.draw_tile(rect, 1, 0)

    def draw_floor(self, rect: Rect):
        self.__resources.tiles2.draw_tile(rect, 1, 3)

    def draw_goal(self, rect: Rect):
        self.__resources.tiles1.draw_tile(rect, 1, 3)

    def draw_wall(self, rect: Rect):
        self.__resources.tiles2.draw_tile(rect, 1, 1)

    @staticmethod
    def number_of_player_phases():
        return 3

    def draw_player(self, rect: Rect, facing: Direction, phase: int):
        if facing == Direction.left:
            self.__resources.tiles3.draw_tile(rect, 3 + phase, 6)
        elif facing == Direction.right:
            self.__resources.tiles3.draw_tile(rect, phase, 6)
        elif facing == Direction.up:
            self.__resources.tiles3.draw_tile(rect, 3 + phase, 4)
        elif facing == Direction.down:
            self.__resources.tiles3.draw_tile(rect, phase, 4)
        else:
            raise ValueError("Unknown direction")

    @staticmethod
    def draw_background(colour: pygame.Color):
        set_background_and_clear(colour)

    @staticmethod
    def update_display():
        pygame.display.flip()
