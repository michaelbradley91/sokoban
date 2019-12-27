from typing import Optional, Tuple

from pygame.rect import Rect

from layouts.layout import Layout, BasicLayout


class AspectLayout(Layout):
    """
    A layout that tries to maintain an aspect ratio for a singular inner layout.
    The inner layout is otherwise centred around the bounding rectangle.
    """

    def __init__(self, aspect_ratio: Tuple[int, int], to_the_nearest: Tuple[int, int] = None,
                 identifier: Optional[str] = None):
        """
        :param aspect_ratio: the aspect ratio in (width, [to] height)
        :param to_the_nearest: in (width, height), integers stating the width and height should be to the nearest
                               width / height coordinates. Again, the layout is centred if needed to account for this.
        :param identifier: the identifier for the layout (defaults to random)

        Note: different values in "to_the_nearest" can force the wrong aspect ratio.
        """
        super().__init__(identifier)
        self.aspect_ratio = aspect_ratio
        self.to_the_nearest = to_the_nearest
        self.layout: Optional[Layout] = None

    def set_layout(self, layout: Layout):
        """
        Set the layout used by the Aspect Layout
        :param layout: the layout to control
        :return: nothing
        """
        self.layout = layout

    def remove_layout(self):
        self.layout = None

    def update_components(self):
        if not self.layout:
            return

        if self.bounding_rect.width == 0 or self.bounding_rect.height == 0:
            self.layout.update_rect(self.bounding_rect)
            return

        # Compute the larger of the two by aspect ratio
        if self.bounding_rect.width / self.bounding_rect.height > self.aspect_ratio[0] / self.aspect_ratio[1]:
            # Too wide - fill the available height
            new_height = int((self.bounding_rect.height // self.to_the_nearest[1]) * self.to_the_nearest[1])
            new_width = int(((new_height * self.aspect_ratio[0] / self.aspect_ratio[1])
                             // self.to_the_nearest[0]) * self.to_the_nearest[0])
        else:
            # Too tall - fill the available width
            new_width = int((self.bounding_rect.width // self.to_the_nearest[0]) * self.to_the_nearest[0])
            new_height = int(((new_width * self.aspect_ratio[1] / self.aspect_ratio[0])
                              // self.to_the_nearest[1]) * self.to_the_nearest[1])

        # Centre in the available space
        offset_x = self.bounding_rect.x + ((self.bounding_rect.width - new_width) // 2)
        offset_y = self.bounding_rect.y + ((self.bounding_rect.height - new_height) // 2)

        self.layout.update_rect(Rect((offset_x, offset_y), (new_width, new_height)))


def test_aspect_layout():
    b = BasicLayout()
    aspect_layout = AspectLayout(aspect_ratio=(3, 4), to_the_nearest=(50, 20))
    aspect_layout.set_layout(b)

    aspect_layout.update_rect(Rect((30, 40), (1220, 2100)))

    assert b.bounding_rect == Rect((40, 290), (1200, 1600))
