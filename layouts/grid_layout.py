from typing import Optional, Dict, Tuple

from pygame.rect import Rect

from coordinate import Coordinate
from layouts.layout import Layout, BasicLayout


class GridLayout(Layout):
    """
    A grid layout will resize individual segments to fit its bounding box exactly.
    Note: if you need to prevent squares being stretched out of shape, then surround this with
    an aspect layout.
    """
    def __init__(self, width: int, height: int, identifier: Optional[str] = None):
        super().__init__(identifier)
        self.grid_width = width
        self.grid_height = height
        self.layouts: Dict[Layout, Tuple[Coordinate, int, int]] = dict()

    def add_layout(self, layout: Layout, position: Coordinate, row_span: int = 1, column_span: int = 1):
        """
        Add a layout to the grid. Layouts ARE allowed to overlap on the grid.

        :param layout: the layout to add
        :param position: the top left square where it should be added
        :param row_span: how many rows to span.
        :param column_span: how many columns to span.
        :return: nothing

        Raises an error if the coordinates combined with row span and column span fall outside of the grid.
        """

        if position.x < 0:
            raise ValueError("X position can not be negative")
        if position.y < 0:
            raise ValueError("Y position can not be negative")
        if row_span <= 0:
            raise ValueError("Cannot span less than one row")
        if column_span <= 0:
            raise ValueError("Cannot span less than one column")
        if position.x + column_span > self.grid_width or position.y + row_span > self.grid_height:
            raise ValueError(f"Out of bounds: position: {position} column span: {column_span} row span: {row_span}")

        self.layouts[layout] = position, row_span, column_span

    def remove_layout(self, layout: Layout):
        """
        Remove the given layout. Does nothing if not present
        :param layout: the layout to remove
        :return: nothing
        """
        self.layouts.pop(layout, None)

    def update_components(self):
        if not self.layouts:
            return

        # Calculate the coordinate positions
        x_markers = [0]
        typical_width = self.bounding_rect.width / self.grid_width
        for x in range(1, self.grid_width + 1):
            x_markers.append(int(x * typical_width))
        x_markers[-1] = self.bounding_rect.width
        for i, x_marker in enumerate(x_markers):
            if x_marker < 0:
                x_markers[i] = 0
            if x_marker > self.bounding_rect.width:
                x_markers[i] = self.bounding_rect.width

        y_markers = [0]
        typical_height = self.bounding_rect.height / self.grid_height
        for y in range(1, self.grid_height + 1):
            y_markers.append(int(y * typical_height))
        y_markers[-1] = self.bounding_rect.height
        for i, y_marker in enumerate(y_markers):
            if y_marker < 0:
                y_markers[i] = 0
            if y_marker > self.bounding_rect.height:
                y_markers[i] = self.bounding_rect.height

        # Update the sizes
        for layout in self.layouts:
            coordinate, row_span, column_span = self.layouts[layout]
            x = x_markers[coordinate.x]
            y = y_markers[coordinate.y]
            width = x_markers[coordinate.x + column_span] - x
            height = y_markers[coordinate.y + row_span] - y
            rect = Rect((self.bounding_rect.x + x, self.bounding_rect.y + y), (width, height))
            layout.update_rect(rect)


def test_grid_layout():
    b1 = BasicLayout()
    b2 = BasicLayout()
    b3 = BasicLayout()

    grid_layout = GridLayout(width=20, height=5)
    grid_layout.add_layout(b1, Coordinate(1, 3))
    grid_layout.add_layout(b2, Coordinate(10, 0), row_span=5, column_span=6)
    grid_layout.add_layout(b3, Coordinate(4, 4), row_span=1, column_span=10)
    grid_layout.update_rect(Rect((15, 200), (300, 400)))

    assert b1.bounding_rect == Rect((30, 440), (15, 80))
    assert b2.bounding_rect == Rect((165, 200), (90, 400))
    assert b3.bounding_rect == Rect((75, 520), (150, 80))



