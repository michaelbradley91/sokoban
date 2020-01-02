from typing import List

from app_container import AppContainer
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from pieces.crate import CratePiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from views.components.component_view import ComponentView, ComponentViewModel
from views.components.menu_text_item_view import MenuTextItemViewModel, MenuTextItemView
from views.components.title_view import TitleView, TitleViewModel


class MenuViewModel(ComponentViewModel):
    """ A menu view model """
    def __init__(self, app_container: AppContainer, grid_width: int, grid_height: int):
        super().__init__(app_container)

        self.__grid = Grid(self.app_container, grid_width, grid_height)
        self.__grid.add_outer_wall()

        self.__menu_items: List[MenuTextItemViewModel] = []
        self.title_view_model = TitleViewModel(self.app_container, self.grid)

    def add_menu_item(self, menu_item: MenuTextItemViewModel):
        self.__menu_items.append(menu_item)

    @property
    def grid(self):
        return self.__grid

    @property
    def menu_items(self) -> List[MenuTextItemViewModel]:
        return self.__menu_items


class MenuView(ComponentView[MenuViewModel, BasicLayout]):
    """
    A menu view which is designed to provide the common elements for any menu page.
    The grid passed should have the correct width and height
    """

    def __init__(self, app_container: AppContainer, model: MenuViewModel, layout: BasicLayout):
        super().__init__(app_container, model, layout)

        # Create the grid layout
        self.grid_layout = GridLayout(width=self.grid.width, height=self.grid.height)

        # Add the square layout
        self.square_layout = BasicLayout()
        self.grid_layout.add_layout(self.square_layout, Coordinate(0, 0))

        # Add the title view
        self.title_view = TitleView(self.app_container, self.model.title_view_model, self.grid_layout)

        # Aspect fit the grid to the outer layout
        aspect_layout = AspectLayout((self.grid_layout.grid_width, self.grid_layout.grid_height),
                                     (self.grid_layout.grid_width, self.grid_layout.grid_height))

        # Menu items
        self.__menu_items: List[MenuTextItemView] = []

        aspect_layout.set_layout(self.grid_layout)
        self.layout.set_layout(aspect_layout)

    def draw_static(self):
        # Draw the grid
        for piece_type in [p for p in PIECE_DRAW_ORDER if p not in [PlayerPiece, CratePiece]]:
            for piece in self.grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        # Draw the title
        self.title_view.draw_static()

        # Draw the menu
        for menu_item in self.__menu_items:
            menu_item.draw_static()

    def draw_animated(self):
        # Draw animated crates and players
        for piece in self.grid.get_pieces_of_type(CratePiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        for piece in self.grid.get_pieces_of_type(PlayerPiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

    @property
    def menu_items(self) -> List[MenuTextItemView]:
        return self.__menu_items

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    @property
    def grid(self):
        return self.model.grid
