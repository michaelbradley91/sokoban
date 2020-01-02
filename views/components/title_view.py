from app_container import AppContainer
from constants.colours import TITLE_COLOUR, TITLE_SHADOW_COLOUR
from constants.text import START_VIEW_TITLE, draw_text_with_border
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from pieces.static import StaticPiece
from views.components.component_view import ComponentView, ComponentViewModel

TITLE_HEIGHT = 2


class TitleViewModel(ComponentViewModel):
    def __init__(self, app_container: AppContainer, grid: Grid):
        super().__init__(app_container)

        self.__grid = grid

        # Add title bricks to the top of the menu
        for y in range(1, TITLE_HEIGHT + 1):
            for x in range(1, grid.width - 1):
                grid.add_piece(StaticPiece(self.grid, self.app_container, self.resources.menu_background),
                               Coordinate(x, y))

    @property
    def grid(self):
        return self.__grid


class TitleView(ComponentView[TitleViewModel, GridLayout]):
    """
    A view for drawing the title text.
    """
    def __init__(self, app_container: AppContainer, model: TitleViewModel, layout: GridLayout):
        super().__init__(app_container, model, layout)

        self.title_layout = BasicLayout()

        surface = self.resources.title_font.get_surface(START_VIEW_TITLE, TITLE_COLOUR)
        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(self.title_layout)

        margin_layout = MarginLayout(1 / 20, identifier="title_margin")
        margin_layout.set_layout(aspect_layout)

        layout.add_layout(margin_layout, Coordinate(1, 1), column_span=self.grid.width - 2, row_span=TITLE_HEIGHT)

    def draw_static(self):
        draw_text_with_border(self.resources.title_font, START_VIEW_TITLE, TITLE_COLOUR,
                              self.title_layout.bounding_rect, TITLE_SHADOW_COLOUR,
                              self.title_layout.bounding_rect.width / 120)

    def draw_animated(self):
        pass

    @property
    def grid(self):
        return self.model.grid
