from typing import TYPE_CHECKING

from app_container import AppContainer
from constants.colours import MENU_SELECTED_TEXT_COLOUR, MENU_TEXT_COLOUR
from constants.numbers import MENU_TEXT_MARGIN, MENU_TEXT_SELECTED_MARGIN
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from pieces.static import StaticPiece
from views.components.component_view import ComponentView, ComponentViewModel

if TYPE_CHECKING:
    from views.components.menu_view import MenuViewModel


class MenuTextItemViewModel(ComponentViewModel):
    """
    A default menu text item
    """
    def __init__(self, app_container: AppContainer, grid: Grid,
                 position: Coordinate, column_span: int, row_span: int = 1):
        super().__init__(app_container)

        self.__position = position
        self.__column_span = column_span
        self.__row_span = row_span

        self.__grid = grid

        self.highlighted = False

        # Add myself to the grid
        for x_offset in range(column_span):
            for y_offset in range(row_span):
                coordinate = position + Coordinate(x_offset, y_offset)
                piece = StaticPiece(self.grid, self.app_container, self.resources.menu_background)
                self.grid.add_piece(piece, coordinate)

    @property
    def grid(self) -> Grid:
        return self.__grid

    @property
    def position(self) -> Coordinate:
        return self.__position

    @property
    def column_span(self):
        return self.__column_span

    @property
    def row_span(self):
        return self.__row_span


class MenuTextItemView(ComponentView[MenuTextItemViewModel, GridLayout]):
    """
    A menu text view item
    """
    def __init__(self, app_container: AppContainer, model: MenuTextItemViewModel, layout: GridLayout, text: str):
        super().__init__(app_container, model, layout)
        self.text = text
        self.grid_layout = layout

        # Create the menu item
        surface = self.resources.menu_font.get_surface(text, MENU_TEXT_COLOUR)

        self.__layout = BasicLayout()

        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(self.__layout)

        self.__margin_layout = MarginLayout(self.get_margin())
        self.__margin_layout.set_layout(aspect_layout)

        self.grid_layout.add_layout(self.__margin_layout, self.model.position,
                                    column_span=self.model.column_span, row_span=self.model.row_span)

    def draw_static(self):
        target_margin = self.get_margin()

        # TODO consider doing this through observables to avoid running it in the draw loop
        if self.__margin_layout.margin != target_margin:
            self.__margin_layout.set_margin(target_margin)
            self.__margin_layout.update_components()

        colour = MENU_SELECTED_TEXT_COLOUR if self.model.highlighted else MENU_TEXT_COLOUR
        self.resources.menu_font.draw_text(self.text, colour, self.__layout.bounding_rect)

    def get_margin(self):
        return MENU_TEXT_SELECTED_MARGIN if self.model.highlighted else MENU_TEXT_MARGIN

    def draw_animated(self):
        pass
