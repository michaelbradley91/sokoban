import pygame
from enum import Enum
from typing import List, Dict, Callable

from pygame.event import EventType

from animator import Animator
from colours import MENU_TEXT_COLOUR, TITLE_COLOUR, BACKGROUND_COLOUR
from coordinate import Coordinate
from direction import Direction
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from music_player import MusicPlayer
from navigator import Navigator
from opengl_support.helpers import set_background_and_clear
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from pieces.wall import WallPiece
from resources import Resources
from text import START_VIEW_START, START_VIEW_OPTIONS, START_VIEW_HELP, START_VIEW_QUIT, START_VIEW_TITLE
from undo import UndoManager
from views.map_view import MapView, MapViewParameters
from views.view import ViewModel, View


class MenuOption(Enum):
    start = START_VIEW_START
    options = START_VIEW_OPTIONS
    help = START_VIEW_HELP
    quit = START_VIEW_QUIT


# noinspection PyTypeChecker
MENU_INDEX_BY_OPTION = {m: i for i, m in enumerate(MenuOption)}
# noinspection PyTypeChecker
MENU_OPTION_BY_INDEX = {i: m for i, m in enumerate(MenuOption)}

TITLE_HEIGHT = 3
GRID_WIDTH = 12
GRID_HEIGHT = TITLE_HEIGHT + 1 + (2 * len(MENU_OPTION_BY_INDEX)) + 1
MENU_OPTION_WIDTH = 4
MENU_OPTION_LEFT = (GRID_WIDTH // 2) - (MENU_OPTION_WIDTH // 2)
MENU_OPTION_RIGHT = MENU_OPTION_LEFT + MENU_OPTION_WIDTH


def menu_option_position(index: int):
    return TITLE_HEIGHT + (index * 2) + 1


class StartViewParameters:
    pass


class StartViewModel(ViewModel[StartViewParameters]):
    def __init__(self, view: "StartView"):
        super().__init__(view)
        self.menu_option_selected = MenuOption.start

        self.undo_manager.enabled = False
        self.grid = Grid(self.undo_manager, self.animator, self.music_player, self.resources, GRID_WIDTH, GRID_HEIGHT)
        self.undo_manager.enabled = True
        self.player_piece = PlayerPiece(self.grid, self.undo_manager, self.animator,
                                        self.music_player, self.resources)
        self.player_piece.direction = Direction.right

        self.load_grid()

    def load_grid(self):
        self.grid.add_outer_wall()

        # Title bricks
        for y in range(1, TITLE_HEIGHT):
            for x in range(1, self.grid.width - 1):
                self.grid.add_piece(WallPiece(self.grid, self.undo_manager, self.animator,
                                              self.music_player, self.resources), Coordinate(x, y))

        # Menu item bricks
        for x in range(MENU_OPTION_LEFT, MENU_OPTION_RIGHT):
            for i in range(0, len(MENU_OPTION_BY_INDEX)):
                y = menu_option_position(i)
                self.grid.add_piece(WallPiece(self.grid, self.undo_manager, self.animator,
                                              self.music_player, self.resources), Coordinate(x, y))

        # Player piece
        self.update_player_piece()

    def update_player_piece(self):
        i = MENU_INDEX_BY_OPTION[self.menu_option_selected]
        x = MENU_OPTION_LEFT - 2
        y = menu_option_position(i)
        self.grid.move_piece(self.player_piece, Coordinate(x, y))

    def go_down_one_menu_option(self):
        """
        Move the menu selection down one
        :return: nothing
        """
        index = MENU_INDEX_BY_OPTION[self.menu_option_selected]
        index = (index + 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_option_selected = MENU_OPTION_BY_INDEX[index]
        self.update_player_piece()

    def go_up_one_menu_option(self):
        """
        Move the menu selection up one
        :return:
        """
        index = MENU_INDEX_BY_OPTION[self.menu_option_selected]
        index = (index + len(MENU_INDEX_BY_OPTION) - 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_option_selected = MENU_OPTION_BY_INDEX[index]
        self.update_player_piece()


class StartView(View[StartViewParameters, StartViewModel]):
    def __init__(self, undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer, resources: Resources,
                 navigator: Navigator, layout: BasicLayout):
        super().__init__(undo_manager, animator, music_player, resources, navigator, layout)

        self.menu_actions: Dict[MenuOption, Callable] = {
            MenuOption.start: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.options: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.help: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.quit: lambda: self.navigator.quit()
        }

        self.menu_layouts: Dict[MenuOption, BasicLayout] = {m: BasicLayout() for m in MenuOption}
        self.title_layout = BasicLayout()
        self.grid_layout = GridLayout(width=GRID_WIDTH, height=GRID_HEIGHT)
        self.square_layout = BasicLayout()

    def init(self):
        # Add the title
        surface = self.resources.title_font.get_surface(START_VIEW_TITLE, TITLE_COLOUR)
        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(self.title_layout)

        margin_layout = MarginLayout((0, 1 / 7))
        margin_layout.set_layout(aspect_layout)

        self.grid_layout.add_layout(margin_layout, Coordinate(0, 0), column_span=GRID_WIDTH, row_span=TITLE_HEIGHT)

        # Build layouts to hold the menu text
        for i, m in MENU_OPTION_BY_INDEX.items():
            surface = self.resources.menu_font.get_surface(m.value, MENU_TEXT_COLOUR)
            aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
            aspect_layout.set_layout(self.menu_layouts[m])

            margin_layout = MarginLayout((0, 1 / 5))
            margin_layout.set_layout(aspect_layout)

            y = menu_option_position(i)
            x = MENU_OPTION_LEFT

            self.grid_layout.add_layout(margin_layout, Coordinate(x, y), column_span=MENU_OPTION_WIDTH)

        self.grid_layout.add_layout(self.square_layout, Coordinate(0, 0))

        aspect_layout = AspectLayout((self.grid_layout.grid_width, self.grid_layout.grid_height),
                                     (self.grid_layout.grid_width, self.grid_layout.grid_height))

        aspect_layout.set_layout(self.grid_layout)
        self.layout.set_layout(aspect_layout)

    def close(self):
        pass

    def pre_event_loop(self):
        pass

    def post_event_loop(self):
        pass

    def on_events(self, events: List[EventType]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.menu_actions[self.model.menu_option_selected]()
                    return

                if event.key == pygame.K_DOWN:
                    self.model.go_down_one_menu_option()

                if event.key == pygame.K_UP:
                    self.model.go_up_one_menu_option()

    def draw(self):
        set_background_and_clear(BACKGROUND_COLOUR)

        # Draw the grid
        for piece_type in PIECE_DRAW_ORDER:
            for piece in self.grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        # Draw the text on top
        for m in MenuOption:
            layout = self.menu_layouts[m]
            text = m.value
            self.resources.menu_font.draw_text(text, MENU_TEXT_COLOUR, layout.bounding_rect)

        # Draw the title
        self.resources.title_font.draw_text(START_VIEW_TITLE, TITLE_COLOUR, self.title_layout.bounding_rect)

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    @property
    def grid(self):
        return self.model.grid
