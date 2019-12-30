from abc import ABC, abstractmethod

from pygame.rect import Rect


class Drawable(ABC):
    """
    An object that can be drawn in a rectangle
    """
    @abstractmethod
    def draw(self, rect: Rect):
        """
        Draw this to fill the given rectangle
        :param rect: the rectangle to fill
        :return: nothing
        """
        pass
