from app_container import AppContainer
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from pieces.crate import CratePiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from pieces.static import StaticPiece
from views.components.component_view import ComponentView
from views.components.title_view import TitleView
from views.start_view import TITLE_HEIGHT


class MenuView(ComponentView[BasicLayout]):
    """
    A menu view which is designed to provide the common elements for any menu page.
    The grid passed should have the correct width and height
    """

    def __init__(self, app_container: AppContainer, layout: BasicLayout, grid: Grid):
        super().__init__(app_container, layout)

        self.__grid = grid

        # Add the walls
        self.__grid.add_outer_wall()

        # Add the title bricks at the top
        for y in range(1, TITLE_HEIGHT + 1):
            for x in range(1, self.__grid.width - 1):
                self.__grid.add_piece(StaticPiece(self.__grid, self.app_container, self.resources.menu_background),
                                      Coordinate(x, y))

        # Create the grid layout
        self.grid_layout = GridLayout(width=self.__grid.width, height=self.__grid.height)

        # Add the square layout
        self.square_layout = BasicLayout()
        self.grid_layout.add_layout(self.square_layout, Coordinate(0, 0))

        # Add the title view
        title_container_layout = BasicLayout()
        self.title_view = TitleView(self.app_container, title_container_layout)
        self.grid_layout.add_layout(title_container_layout, Coordinate(1, 1),
                                    column_span=self.__grid.width - 2, row_span=TITLE_HEIGHT)

        # Aspect fit the grid to the outer layout
        aspect_layout = AspectLayout((self.grid_layout.grid_width, self.grid_layout.grid_height),
                                     (self.grid_layout.grid_width, self.grid_layout.grid_height))

        aspect_layout.set_layout(self.grid_layout)
        self.layout.set_layout(aspect_layout)

    def draw_static(self):
        # Draw the grid
        for piece_type in [p for p in PIECE_DRAW_ORDER if p not in [PlayerPiece, CratePiece]]:
            for piece in self.__grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        # Draw the title
        self.title_view.draw_static()

    def draw_animated(self):
        pass

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    @property
    def grid(self):
        return self.__grid
