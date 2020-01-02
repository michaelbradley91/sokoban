from enum import Enum
from time import time
from typing import List, Dict, Callable, Optional

import pygame
from pygame.event import EventType

from animations.preset_animation import PresetGridAnimationPlayer, PresetGridAnimation
from app_container import AppContainer
from constants.colours import MENU_TEXT_COLOUR, TITLE_COLOUR, BACKGROUND_COLOUR, MENU_SELECTED_TEXT_COLOUR, \
    TITLE_SHADOW_COLOUR
from constants.direction import Direction
from constants.text import START_VIEW_START, START_VIEW_OPTIONS, START_VIEW_HELP, START_VIEW_QUIT, START_VIEW_TITLE, \
    draw_text_with_border
from coordinate import Coordinate
from grid import Grid
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from opengl_support.helpers import set_background_and_clear
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from pieces.static import StaticPiece
from pieces.wall import WallPiece
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

TITLE_HEIGHT = 2
GRID_WIDTH = 12
GRID_HEIGHT = TITLE_HEIGHT + 2 + (2 * len(MENU_OPTION_BY_INDEX)) + 1
MENU_OPTION_WIDTH = 4
MENU_OPTION_LEFT = (GRID_WIDTH // 2) - (MENU_OPTION_WIDTH // 2)
MENU_OPTION_RIGHT = MENU_OPTION_LEFT + MENU_OPTION_WIDTH - 1
START_MENU_POSITION = "start_position"
START_WAIT_SECONDS = 1
FINISHED_WAIT_SECONDS = 3


def menu_option_position(index: int):
    return TITLE_HEIGHT + (index * 2) + 1 + 1


class StartViewParameters:
    pass


class StartViewModel(ViewModel[StartViewParameters]):
    def __init__(self, view: "StartView"):
        super().__init__(view)
        self.menu_option_selected = MenuOption.start

        self.undo_manager.enabled = False
        self.grid = Grid(self.app_container, GRID_WIDTH, GRID_HEIGHT)

        self.player_piece = PlayerPiece(self.grid, self.app_container)
        self.player_piece.direction = Direction.left

        self.crate_piece = CratePiece(self.grid, self.app_container)

        self.resources.crate_sound.set_volume(0)

        self.player_animation_player: Optional[PresetGridAnimationPlayer] = None

        self.load_grid()
        self.undo_manager.enabled = True
        self.undo_manager.save_position(START_MENU_POSITION)

    def load_grid(self):
        self.grid.add_outer_wall()

        # Player
        player_animation = PresetGridAnimation(Coordinate(MENU_OPTION_LEFT - 2, menu_option_position(0)))
        self.grid.add_piece(self.player_piece, player_animation.steps[0])

        # Title bricks
        for y in range(1, TITLE_HEIGHT + 1):
            for x in range(1, self.grid.width - 1):
                self.grid.add_piece(StaticPiece(self.grid, self.app_container, self.resources.menu_background),
                                    Coordinate(x, y))

        # Menu item bricks
        for x in range(MENU_OPTION_LEFT, MENU_OPTION_RIGHT + 1):
            for i in range(0, len(MENU_OPTION_BY_INDEX)):
                y = menu_option_position(i)
                self.grid.add_piece(StaticPiece(self.grid, self.app_container, self.resources.menu_background),
                                    Coordinate(x, y))

        # Regular wall. We alternate blocked off positions every 2 menu items, starting with the second...
        for i in range(1, len(MENU_OPTION_BY_INDEX), 2):
            y = menu_option_position(i)
            if (i + 1) % 4 == 0:
                # Wall on the right
                r = range(MENU_OPTION_RIGHT + 1, GRID_WIDTH - 1)
            else:
                # Wall on the left
                r = range(1, MENU_OPTION_LEFT)
            for x in r:
                self.grid.add_piece(WallPiece(self.grid, self.app_container), Coordinate(x, y))

        # Crate
        self.grid.add_piece(self.crate_piece, Coordinate(2, menu_option_position(1) - 1))

        # Goal
        self.grid.add_piece(GoalPiece(self.grid, self.app_container), Coordinate(GRID_WIDTH - 2, GRID_HEIGHT - 2))

        # Player loop
        # Around the crate
        player_animation.append_steps(Direction.left, Direction.down)

        # Slide around...
        final_i = list(range(1, len(MENU_OPTION_BY_INDEX), 2))[-1]
        for i in list(range(1, len(MENU_OPTION_BY_INDEX), 2)):
            if (i + 1) % 4 == 0:
                # Moving to the left
                player_animation.append_step(Direction.left, repeat=MENU_OPTION_WIDTH + 3)
                player_animation.append_steps(Direction.up, Direction.left, Direction.down, Direction.down)

                if i != final_i:
                    player_animation.append_steps(Direction.down, Direction.down)
                player_animation.append_steps(Direction.left, Direction.down)

                if i == final_i:
                    # Finish by sliding it over to the right
                    player_animation.append_step(Direction.right, repeat=MENU_OPTION_WIDTH + 4)
            else:
                # Moving to the right
                player_animation.append_step(Direction.right, repeat=MENU_OPTION_WIDTH + 3)
                player_animation.append_steps(Direction.up, Direction.right, Direction.down, Direction.down,
                                              Direction.down, Direction.down, Direction.right, Direction.down)

        self.player_animation_player = player_animation.create_player()

    def go_down_one_menu_option(self):
        """
        Move the menu selection down one
        :return: nothing
        """
        index = MENU_INDEX_BY_OPTION[self.menu_option_selected]
        index = (index + 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_option_selected = MENU_OPTION_BY_INDEX[index]

    def go_up_one_menu_option(self):
        """
        Move the menu selection up one
        :return:
        """
        index = MENU_INDEX_BY_OPTION[self.menu_option_selected]
        index = (index + len(MENU_INDEX_BY_OPTION) - 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_option_selected = MENU_OPTION_BY_INDEX[index]


class StartView(View[StartViewParameters, StartViewModel]):
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

        from views.map_view import MapView, MapViewParameters

        self.menu_actions: Dict[MenuOption, Callable] = {
            MenuOption.start: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.options: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.help: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            MenuOption.quit: lambda: self.navigator.quit()
        }

        self.menu_layouts: Dict[MenuOption, BasicLayout] = {m: BasicLayout() for m in MenuOption}
        self.menu_margin_layouts: Dict[MenuOption, MarginLayout] = {m: MarginLayout((0, 1 / 5)) for m in MenuOption}
        self.title_layout = BasicLayout()
        self.grid_layout = GridLayout(width=GRID_WIDTH, height=GRID_HEIGHT)
        self.square_layout = BasicLayout()
        self.position_won_time = None
        self.position_start_time = None

    def init(self):
        # Add the title
        surface = self.resources.title_font.get_surface(START_VIEW_TITLE, TITLE_COLOUR)
        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(self.title_layout)

        margin_layout = MarginLayout((0, 1 / 20))
        margin_layout.set_layout(aspect_layout)

        self.grid_layout.add_layout(margin_layout, Coordinate(0, 1), column_span=GRID_WIDTH, row_span=TITLE_HEIGHT)

        # Build layouts to hold the menu text
        for i, m in MENU_OPTION_BY_INDEX.items():
            surface = self.resources.menu_font.get_surface(m.value, MENU_TEXT_COLOUR)
            aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
            aspect_layout.set_layout(self.menu_layouts[m])

            self.menu_margin_layouts[m].set_layout(aspect_layout)

            y = menu_option_position(i)
            x = MENU_OPTION_LEFT

            self.grid_layout.add_layout(self.menu_margin_layouts[m], Coordinate(x, y), column_span=MENU_OPTION_WIDTH)

        self.grid_layout.add_layout(self.square_layout, Coordinate(0, 0))

        aspect_layout = AspectLayout((self.grid_layout.grid_width, self.grid_layout.grid_height),
                                     (self.grid_layout.grid_width, self.grid_layout.grid_height))

        aspect_layout.set_layout(self.grid_layout)
        self.layout.set_layout(aspect_layout)
        self.position_start_time = time()

        self.resources.crate_sound.set_volume(0)

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

                elif event.key == pygame.K_DOWN:
                    self.model.go_down_one_menu_option()

                elif event.key == pygame.K_UP:
                    self.model.go_up_one_menu_option()

    def draw_static(self):
        for m, margin_layout in self.menu_margin_layouts.items():
            if self.model.menu_option_selected == m:
                margin_layout.set_margin((0, 1 / 7))
            else:
                margin_layout.set_margin((0, 1 / 5))
            margin_layout.update_components()

        set_background_and_clear(BACKGROUND_COLOUR)

        # Draw the grid
        for piece_type in [p for p in PIECE_DRAW_ORDER if p not in [PlayerPiece, CratePiece]]:
            for piece in self.grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        # Draw the text on top
        for m in MenuOption:
            layout = self.menu_layouts[m]
            text = m.value
            colour = MENU_SELECTED_TEXT_COLOUR if m == self.model.menu_option_selected else MENU_TEXT_COLOUR
            self.resources.menu_font.draw_text(text, colour, layout.bounding_rect)

        # Draw the title
        draw_text_with_border(self.resources.title_font, START_VIEW_TITLE, TITLE_COLOUR,
                              self.title_layout.bounding_rect, TITLE_SHADOW_COLOUR,
                              self.title_layout.bounding_rect.width / 120)

    def post_animation_loop(self):
        if self.animator.animating():
            return

        if self.position_won_time:
            now = time()
            if now - self.position_won_time >= FINISHED_WAIT_SECONDS:
                self.position_won_time = False
                self.undo_manager.undo(START_MENU_POSITION)
                self.model.player_animation_player.reset()
                self.position_start_time = time()
        elif self.position_start_time:
            now = time()
            if now - self.position_start_time >= START_WAIT_SECONDS:
                self.position_start_time = None
        elif self.model.player_animation_player.is_finished:
            self.position_won_time = time()
        else:
            # Next position for the player...
            self.model.player_piece.move(self.model.player_animation_player.play_next_step())

    def draw_animated(self):
        for piece in self.grid.get_pieces_of_type(CratePiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        for piece in self.grid.get_pieces_of_type(PlayerPiece):
            piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    @property
    def grid(self):
        return self.model.grid
