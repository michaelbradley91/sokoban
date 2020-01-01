from typing import Union, Tuple, Optional

from pygame.rect import Rect

from layouts.layout import Layout, BasicLayout


def translate_margin(margin: Union[float, Tuple[float, float], Tuple[float, float, float, float]]) -> \
        Tuple[float, float, float, float]:
    """
    Translates a margin as follows:
    - 1 value = the same for all 4 sides
    - 2 values = the first is left and right, and the second is top and bottom
    - 4 values = left, top, right, bottom
    :param margin:
    :return: nothing
    """
    if isinstance(margin, float):
        return margin, margin, margin, margin

    if len(margin) == 1:
        return margin[0], margin[0], margin[0], margin[0]

    if len(margin) == 2:
        return margin[0], margin[1], margin[0], margin[1]

    if len(margin) != 4:
        raise ValueError("Invalid margin format")
    return margin


class MarginLayout(Layout):
    """
    A simple layout that places a percentage margin on each side of itself
    """

    def __init__(self, margin: Union[float, Tuple[float, float], Tuple[float, float, float, float]],
                 identifier: Optional[str] = None):
        super().__init__(identifier)

        self.left_margin = None
        self.top_margin = None
        self.right_margin = None
        self.bottom_margin = None
        self.set_margin(margin)

        self.layout: Optional[Layout] = None

    def set_margin(self, margin: Union[float, Tuple[float, float], Tuple[float, float, float, float]]):
        translated_margin = translate_margin(margin)
        if any([m for m in translated_margin if m < 0]):
            raise ValueError("Invalid margins!")

        self.left_margin = translated_margin[0]
        self.top_margin = translated_margin[1]
        self.right_margin = translated_margin[2]
        self.bottom_margin = translated_margin[3]

    def set_layout(self, layout: Layout):
        """
        Set the layout used by the Margin Layout
        :param layout: the layout to control
        :return: nothing
        """
        self.layout = layout

    def remove_layout(self):
        self.layout = None

    def update_components(self):
        if not self.layout:
            return

        # Check if invisible
        if self.left_margin + self.right_margin > 1 or self.top_margin + self.bottom_margin > 1:
            self.layout.update_rect(Rect((self.bounding_rect.x, self.bounding_rect.y), (0, 0)))

        # Compute the boundaries...
        left_m = int(self.left_margin * self.bounding_rect.width)
        right_m = int(self.right_margin * self.bounding_rect.width)
        top_m = int(self.top_margin * self.bounding_rect.height)
        bottom_m = int(self.bottom_margin * self.bounding_rect.height)

        # Compute the rectangle
        x = self.bounding_rect.x + left_m
        y = self.bounding_rect.y + top_m
        width = self.bounding_rect.width - (left_m + right_m)
        height = self.bounding_rect.height - (top_m + bottom_m)

        self.layout.update_rect(Rect((x, y), (width, height)))


def test_margin_layout():
    b = BasicLayout()
    margin_layout = MarginLayout((0.2, 0.3, 0.4, 0.5))
    margin_layout.set_layout(b)
    margin_layout.update_rect(Rect((20, 30), (200, 100)))

    assert b.bounding_rect == Rect((60, 60), (80, 20))
