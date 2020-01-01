from typing import Optional, Dict, List

from pygame.rect import Rect

from constants.direction import Direction
from layouts.layout import Layout, BasicLayout


class LinearLayout(Layout):
    """
    A linear layout places objects in a particular direction in a line.
    """

    def __init__(self, direction: Direction, identifier: Optional[str] = None):
        super().__init__(identifier)
        self.direction = direction
        self.layouts: List[Layout] = []
        self.percentage_by_layout: Dict[Layout, float] = dict()

    def add_layout(self, layout: Layout, percentage: float, insertion_index: int = -1):
        """
        Add a layout to this one, specifying how much of the distance it
        should occupy down its length as a percentage.
        :param layout: the layout itself.
        :param percentage: the percentage to occupy down the length of the layout
        :param insertion_index: where along the layout this should be inserted.
                                -1 means the end which is the default.
        :return: nothing.

        Raises an error if the percentage occupied rises above 100%.
        """
        total_percent = sum(self.percentage_by_layout.values()) + percentage
        if total_percent > 1.0001:
            raise ValueError("Percentage cannot rise above 100%")

        if insertion_index < 0:
            self.layouts.append(layout)
        else:
            self.layouts.insert(insertion_index, layout)
        self.percentage_by_layout[layout] = percentage

    def remove_layout(self, layout: Layout):
        """
        Remove a layout. Does nothing if the layout does not exist
        """
        if layout in self.percentage_by_layout:
            self.percentage_by_layout.pop(layout)
            self.layouts.remove(layout)

    def update_components(self):
        if not self.layouts:
            return

        current_percentage = 0
        total_length = self.bounding_rect.width if self.direction in [Direction.left, Direction.right] \
            else self.bounding_rect.height
        markers: List[int] = [0]

        # Compute the markers
        for layout in self.layouts:
            next_percentage = self.percentage_by_layout[layout] + current_percentage
            markers.append(int(next_percentage * total_length))
            current_percentage = next_percentage

        # Fit the markers
        for i, m in list(enumerate(markers)):
            if m < 0:
                markers[i] = 0
            if m > total_length:
                markers[i] = total_length

        # Apply the rectangles
        for start, end, layout in zip(markers, markers[1:], self.layouts):
            if self.direction == Direction.right:
                layout.update_rect(Rect((self.bounding_rect.x + start, self.bounding_rect.y),
                                        (end - start, self.bounding_rect.height)))
            if self.direction == Direction.left:
                layout.update_rect(Rect((self.bounding_rect.x + self.bounding_rect.width - end, self.bounding_rect.y),
                                        (end - start, self.bounding_rect.height)))
            if self.direction == Direction.down:
                layout.update_rect(Rect((self.bounding_rect.x, self.bounding_rect.y + start),
                                        (self.bounding_rect.width, end - start)))
            if self.direction == Direction.up:
                layout.update_rect(Rect((self.bounding_rect.x, self.bounding_rect.y + self.bounding_rect.height - end),
                                        (self.bounding_rect.width, end - start)))


def test_linear_layout_left():
    linear_layout = LinearLayout(direction=Direction.left)
    b1 = BasicLayout()
    b2 = BasicLayout()
    b3 = BasicLayout()
    b4 = BasicLayout()

    linear_layout.add_layout(b1, 0.1)
    linear_layout.add_layout(b2, 0.3)
    linear_layout.add_layout(b3, 0.1)
    linear_layout.add_layout(b4, 0.5)

    linear_layout.update_rect(Rect((10, 20), (50, 200)))

    assert b1.bounding_rect == Rect((55, 20), (5, 200))
    assert b2.bounding_rect == Rect((40, 20), (15, 200))
    assert b3.bounding_rect == Rect((35, 20), (5, 200))
    assert b4.bounding_rect == Rect((10, 20), (25, 200))


def test_linear_layout_right():
    linear_layout = LinearLayout(direction=Direction.right)
    b1 = BasicLayout()
    b2 = BasicLayout()
    b3 = BasicLayout()
    b4 = BasicLayout()

    linear_layout.add_layout(b1, 0.1)
    linear_layout.add_layout(b2, 0.3)
    linear_layout.add_layout(b3, 0.1)
    linear_layout.add_layout(b4, 0.5)

    linear_layout.update_rect(Rect((10, 20), (50, 200)))

    assert b1.bounding_rect == Rect((10, 20), (5, 200))
    assert b2.bounding_rect == Rect((15, 20), (15, 200))
    assert b3.bounding_rect == Rect((30, 20), (5, 200))
    assert b4.bounding_rect == Rect((35, 20), (25, 200))


def test_linear_layout_down():
    linear_layout = LinearLayout(direction=Direction.down)
    b1 = BasicLayout()
    b2 = BasicLayout()
    b3 = BasicLayout()
    b4 = BasicLayout()

    linear_layout.add_layout(b1, 0.1)
    linear_layout.add_layout(b2, 0.3)
    linear_layout.add_layout(b3, 0.1)
    linear_layout.add_layout(b4, 0.5)

    linear_layout.update_rect(Rect((10, 20), (50, 200)))

    assert b1.bounding_rect == Rect((10, 20), (50, 20))
    assert b2.bounding_rect == Rect((10, 40), (50, 60))
    assert b3.bounding_rect == Rect((10, 100), (50, 20))
    assert b4.bounding_rect == Rect((10, 120), (50, 100))


def test_linear_layout_up():
    linear_layout = LinearLayout(direction=Direction.up)
    b1 = BasicLayout()
    b2 = BasicLayout()
    b3 = BasicLayout()
    b4 = BasicLayout()

    linear_layout.add_layout(b1, 0.1)
    linear_layout.add_layout(b2, 0.3)
    linear_layout.add_layout(b3, 0.1)
    linear_layout.add_layout(b4, 0.5)

    linear_layout.update_rect(Rect((10, 20), (50, 200)))

    assert b1.bounding_rect == Rect((10, 200), (50, 20))
    assert b2.bounding_rect == Rect((10, 140), (50, 60))
    assert b3.bounding_rect == Rect((10, 120), (50, 20))
    assert b4.bounding_rect == Rect((10, 20), (50, 100))
