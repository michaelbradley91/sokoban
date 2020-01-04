from enum import Enum
from time import time
from typing import List, Dict, Callable, Optional

import pygame
from pygame.event import EventType

from animations.preset_animation import PresetGridAnimationPlayer, PresetGridAnimation
from app_container import AppContainer
from constants.colours import BACKGROUND_COLOUR
from constants.direction import Direction
from constants.text import START_VIEW_START, START_VIEW_OPTIONS, START_VIEW_HELP, START_VIEW_QUIT
from coordinate import Coordinate
from layouts.layout import BasicLayout
from opengl_support.helpers import set_background_and_clear
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.player import PlayerPiece
from pieces.wall import WallPiece
from views.components.menu_text_item_view import MenuTextItemViewModel, MenuTextItemView
from views.components.menu_view import MenuView, MenuViewModel
from views.components.title_view import TITLE_HEIGHT
from views.view import ViewModel, View


class MenuOption(Enum):
    start = START_VIEW_START
    options = START_VIEW_OPTIONS
    help = START_VIEW_HELP
    quit = START_VIEW_QUIT


# noinspection PyTypeChecker
MENU_INDEX_BY_OPTION: Dict[MenuOption, int] = {m: i for i, m in enumerate(MenuOption)}
# noinspection PyTypeChecker
MENU_OPTION_BY_INDEX: Dict[int, MenuOption] = {i: m for i, m in enumerate(MenuOption)}

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
        self.resources.crate_sound.set_volume(0)
        self.undo_manager.enabled = False
        self.menu_view_model = MenuViewModel(self.app_container, GRID_WIDTH, GRID_HEIGHT)

        # Add menu options
        for i, m in MENU_OPTION_BY_INDEX.items():
            x = MENU_OPTION_LEFT
            y = menu_option_position(i)
            menu_item_view_model = MenuTextItemViewModel(self.app_container, self.menu_view_model.grid,
                                                         Coordinate(x, y), column_span=MENU_OPTION_WIDTH)
            self.menu_view_model.add_menu_item(menu_item_view_model)

        self.menu_index_selected: int = 0
        self.menu_items[self.menu_index_selected].highlighted = True

        self.player_piece = PlayerPiece(self.grid, self.app_container)
        self.player_piece.direction = Direction.left

        self.crate_piece = CratePiece(self.grid, self.app_container)
        self.player_animation_player: Optional[PresetGridAnimationPlayer] = None

        self.load_grid()
        self.undo_manager.enabled = True

    def load_grid(self):
        # Player
        player_animation = PresetGridAnimation(Coordinate(MENU_OPTION_LEFT - 2, menu_option_position(0)))
        self.grid.add_piece(self.player_piece, player_animation.steps[0])

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
        self.menu_items[self.menu_index_selected].highlighted = False
        self.menu_index_selected = (self.menu_index_selected + 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_items[self.menu_index_selected].highlighted = True

    def go_up_one_menu_option(self):
        """
        Move the menu selection up one
        :return:
        """
        self.menu_items[self.menu_index_selected].highlighted = False
        new_index = (self.menu_index_selected + len(MENU_INDEX_BY_OPTION) - 1) % len(MENU_INDEX_BY_OPTION)
        self.menu_index_selected = new_index
        self.menu_items[self.menu_index_selected].highlighted = True

    @property
    def grid(self):
        return self.menu_view_model.grid

    @property
    def menu_items(self) -> List[MenuTextItemViewModel]:
        return self.menu_view_model.menu_items


class StartView(View[StartViewParameters, StartViewModel]):
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

        from views.map_view import MapView, MapViewParameters
        from views.options_view import OptionsView, OptionsViewParameters

        self.menu_actions: Dict[int, Callable] = {
            0: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            1: lambda: self.navigator.go_to_view(OptionsView, OptionsViewParameters()),
            2: lambda: self.navigator.go_to_view(MapView, MapViewParameters(map_index=0)),
            3: lambda: self.navigator.quit()
        }

        self.menu_view: Optional[MenuView] = None
        self.position_won_time = None
        self.position_start_time = None

    def init(self):
        menu_container_layout = BasicLayout()
        self.menu_view = MenuView(self.app_container, self.model.menu_view_model, menu_container_layout)

        # Add menu items
        for i, m in MENU_OPTION_BY_INDEX.items():
            model = self.model.menu_items[i]
            menu_item_view = MenuTextItemView(self.app_container, model, self.menu_view.grid_layout, m.value)
            self.menu_view.menu_items.append(menu_item_view)

        self.layout.set_layout(menu_container_layout)
        self.position_start_time = time()
        self.resources.crate_sound.set_volume(0)

        self.undo_manager.save_position(START_MENU_POSITION)

    def close(self):
        pass

    def pre_event_loop(self):
        pass

    def on_events(self, events: List[EventType]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.menu_actions[self.model.menu_index_selected]()
                    return

                elif event.key == pygame.K_DOWN:
                    self.model.go_down_one_menu_option()

                elif event.key == pygame.K_UP:
                    self.model.go_up_one_menu_option()

    def post_event_loop(self):
        pass

    def draw_static(self):
        set_background_and_clear(BACKGROUND_COLOUR)
        self.menu_view.draw_static()

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
        self.menu_view.draw_animated()

    @property
    def grid(self):
        return self.model.grid

    @property
    def grid_layout(self):
        return self.menu_view.grid_layout
