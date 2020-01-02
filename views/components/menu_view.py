from typing import List

from app_container import AppContainer
from constants.colours import MENU_TEXT_COLOUR, MENU_SELECTED_TEXT_COLOUR
from constants.numbers import MENU_TEXT_SELECTED_MARGIN, MENU_TEXT_MARGIN
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from pieces.crate import CratePiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from pieces.static import StaticPiece
from resources import Resources
from views.components.component_view import ComponentView
from views.components.title_view import TitleView

TITLE_HEIGHT = 2


class MenuTextItem:
    """
    A simple menu item that can be highlighted or not
    """
    def __init__(self, resources: Resources, text: str, margin_layout: MarginLayout, layout: BasicLayout):
        self.resources = resources
        self.__margin_layout = margin_layout
        self.text = text
        self.__layout = layout
        self.__highlighted = False

    @property
    def highlighted(self):
        return self.__highlighted

    @highlighted.setter
    def highlighted(self, value):
        # Update the margin
        if value != self.__highlighted:
            if value:
                self.__margin_layout.set_margin((0, MENU_TEXT_SELECTED_MARGIN))
            else:
                self.__margin_layout.set_margin((0, MENU_TEXT_MARGIN))
            self.__margin_layout.update_components()
        self.__highlighted = value

    def draw(self):
        colour = MENU_SELECTED_TEXT_COLOUR if self.highlighted else MENU_TEXT_COLOUR
        self.resources.menu_font.draw_text(self.text, colour, self.__layout.bounding_rect)


class MenuView(ComponentView[BasicLayout]):
    """
    A menu view which is designed to provide the common elements for any menu page.
    The grid passed should have the correct width and height
    """

    def __init__(self, app_container: AppContainer, layout: BasicLayout, grid: Grid):
        super().__init__(app_container, layout)

        self.__menu_items: List[MenuTextItem] = []
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

    def add_menu_item(self, text: str, position: Coordinate, column_span: int, row_span: int = 1) -> MenuTextItem:
        """
        Add a menu item to the view. Fills the grid and will draw appropriately.
        :param text: the text to draw
        :param position: where to position it on the grid's coordinates
        :param column_span: the column span
        :param row_span: the row span (defaults to 1)
        :return: the menu item added
        """

        # Fill the appropriate portion of the grid with menu wall
        for x_offset in range(column_span):
            for y_offset in range(row_span):
                coordinate = position + Coordinate(x_offset, y_offset)
                piece = StaticPiece(self.__grid, self.app_container, self.resources.menu_background)
                self.grid.add_piece(piece, coordinate)

        # Create the menu item
        margin_layout = MarginLayout(MENU_TEXT_MARGIN)
        basic_layout = BasicLayout()
        menu_text_item = MenuTextItem(self.resources, text, margin_layout, basic_layout)

        surface = self.resources.menu_font.get_surface(text, MENU_TEXT_COLOUR)
        # Technically assumes the aspect ratio does not change with colour
        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(basic_layout)

        margin_layout.set_layout(aspect_layout)

        self.grid_layout.add_layout(margin_layout, position, column_span=column_span, row_span=row_span)

        self.__menu_items.append(menu_text_item)
        return menu_text_item

    def draw_static(self):
        # Draw the grid
        for piece_type in [p for p in PIECE_DRAW_ORDER if p not in [PlayerPiece, CratePiece]]:
            for piece in self.__grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        # Draw the title
        self.title_view.draw_static()

        # Draw the menu
        for menu_item in self.__menu_items:
            menu_item.draw()

    def draw_animated(self):
        # Draw animated crates and players
        for piece in self.grid.get_pieces_of_type(CratePiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        for piece in self.grid.get_pieces_of_type(PlayerPiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

    @property
    def menu_items(self) -> List[MenuTextItem]:
        return list(self.__menu_items)

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    @property
    def grid(self):
        return self.__grid
