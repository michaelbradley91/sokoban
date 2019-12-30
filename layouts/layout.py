from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4

from pygame.rect import Rect


class Layout(ABC):
    """
    Represents the base class of a layout
    """
    def __init__(self, identifier: Optional[str] = None):
        self.__rect: Rect = Rect((0, 0), (0, 0))
        self.__identifier = identifier

        if self.__identifier is None:
            self.__identifier = str(uuid4())

    @property
    def identifier(self):
        return self.__identifier

    @property
    def bounding_rect(self) -> Rect:
        return self.__rect

    def update_rect(self, rect: Rect):
        """
        Update the layout's bounding size. This should trigger any layouts within this layout
        to update as well.
        """
        self.__rect = rect
        self.update_components()

    def adjust_to_bounds(self, rect: Rect):
        """
        Adjust a rectangle to the bounds of this layout, so that it fits inside.
        A rectangle completely out of bounds will become emtpy.
        """
        new_x, new_y, new_width, new_height = rect.x, rect.y, rect.width, rect.height
        if rect.x < self.bounding_rect.x:
            new_width = new_width - (self.bounding_rect.x - rect.x)
            if new_width < 0:
                new_width = 0
            new_x = self.bounding_rect.x

        if new_x + new_width > self.bounding_rect.x + self.bounding_rect.width:
            new_width = self.bounding_rect.x + self.bounding_rect.width - new_x
            if new_width < 0:
                new_width = 0

        if rect.y < self.bounding_rect.y:
            new_height = new_height - (self.bounding_rect.y - rect.y)
            if new_height < 0:
                new_height = 0
            new_y = self.bounding_rect.y

        if new_y + new_height > self.bounding_rect.y + self.bounding_rect.height:
            new_height = self.bounding_rect.y + self.bounding_rect.height - new_y
            if new_height < 0:
                new_height = 0

        return Rect((new_x, new_y), (new_width, new_height))

    @abstractmethod
    def update_components(self):
        pass

    def __eq__(self, other):
        if other is self:
            return True

        if isinstance(other, Layout):
            return other.identifier == self.identifier

        return False

    def __hash__(self):
        return self.__identifier.__hash__()


class BasicLayout(Layout):
    def __init__(self, identifier: Optional[str] = None):
        super().__init__(identifier)
        self.layout: Optional[Layout] = None

    def set_layout(self, layout: Layout):
        """
        Set the layout used by the Basic Layout
        :param layout: the layout to control
        :return: nothing
        """
        self.layout = layout

    def remove_layout(self):
        self.layout = None

    def update_components(self):
        if not self.layout:
            return

        self.layout.update_rect(self.bounding_rect)
