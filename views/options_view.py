import pygame
from enum import Enum
from time import time
from typing import List, Dict, Optional, Callable

from pygame.event import EventType

from animations.preset_animation import PresetGridAnimationPlayer, PresetGridAnimation
from app_container import AppContainer
from constants.colours import BACKGROUND_COLOUR
from constants.direction import Direction
from constants.text import OPTIONS_VIEW_CONTROLS, OPTIONS_VIEW_BACK, OPTIONS_VIEW_GRAPHICS, OPTIONS_VIEW_SOUND
from coordinate import Coordinate
from layouts.layout import BasicLayout
from opengl_support.helpers import set_background_and_clear
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.player import PlayerPiece
from pieces.wall import WallPiece
from views.components.menu_text_item_view import MenuTextItemViewModel, MenuTextItemView
from views.components.menu_view import MenuViewModel, MenuView
from views.components.title_view import TITLE_HEIGHT
from views.view import View, ViewModel


class MenuOption(Enum):
    controls = OPTIONS_VIEW_CONTROLS
    sound = OPTIONS_VIEW_SOUND
    graphics = OPTIONS_VIEW_GRAPHICS
    back = OPTIONS_VIEW_BACK


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


class OptionsViewParameters:
    pass


class OptionsViewModel(ViewModel[OptionsViewParameters]):
    def __init__(self, view: "OptionsView"):
        super().__init__(view)
        self.resources.crate_sound.set_volume(0)
        self.player1_animation_player: Optional[PresetGridAnimationPlayer] = None
        self.player2_animation_player: Optional[PresetGridAnimationPlayer] = None

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

        self.player1_piece = PlayerPiece(self.grid, self.app_container)
        self.player1_piece.direction = Direction.left

        self.player2_piece = PlayerPiece(self.grid, self.app_container)
        self.player2_piece.direction = Direction.down

        self.crate_piece = CratePiece(self.grid, self.app_container)

        self.load_grid()
        self.undo_manager.enabled = True

    def load_grid(self):
        # Load both players' start positions
        player1_animation = PresetGridAnimation(Coordinate(MENU_OPTION_LEFT - 2, menu_option_position(0)))
        player2_animation = PresetGridAnimation(Coordinate(MENU_OPTION_RIGHT + 2, menu_option_position(0)))

        self.grid.add_piece(self.player1_piece, player1_animation.steps[0])
        self.grid.add_piece(self.player2_piece, player2_animation.steps[0])

        for i in range(2):
            self.grid.add_piece(WallPiece(self.grid, self.app_container),
                                Coordinate(1, menu_option_position(0) + i - 1))
            self.grid.add_piece(WallPiece(self.grid, self.app_container),
                                Coordinate(GRID_WIDTH - 2, menu_option_position(0) + i - 1))

        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_RIGHT + 1, menu_option_position(1)))

        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_LEFT - 1, menu_option_position(1)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_LEFT - 1, menu_option_position(2)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_RIGHT + 1, menu_option_position(2)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_RIGHT + 2, menu_option_position(2)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_LEFT - 1, menu_option_position(3)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_LEFT - 2, menu_option_position(3)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_RIGHT + 1, menu_option_position(3)))
        self.grid.add_piece(WallPiece(self.grid, self.app_container),
                            Coordinate(MENU_OPTION_RIGHT + 2, menu_option_position(3)))

        # Crate
        self.grid.add_piece(self.crate_piece, Coordinate(MENU_OPTION_LEFT - 1, menu_option_position(1) - 1))

        # Goal
        self.grid.add_piece(GoalPiece(self.grid, self.app_container), Coordinate(GRID_WIDTH - 2, GRID_HEIGHT - 2))

        # Player 1 push right
        player1_animation.append_steps(Direction.down)
        player1_animation.append_step(Direction.right, repeat=MENU_OPTION_WIDTH + 2)
        # Player 2 wait
        player2_animation.append_still(repeat=len(player1_animation.steps) - 1)

        # Player 2 push left
        player2_animation.append_step(Direction.down, repeat=menu_option_position(1) - menu_option_position(0))
        player2_animation.append_steps(Direction.right, Direction.down)
        player2_animation.append_step(Direction.left, repeat=MENU_OPTION_WIDTH + 3)

        # Player 1 push right
        player1_animation.append_step(Direction.left, repeat=MENU_OPTION_WIDTH + 2)
        player1_animation.append_step(Direction.down)
        # Player 1 wait
        player1_animation.append_still(repeat=len(player2_animation.steps) - len(player1_animation.steps))

        player1_animation.append_step(Direction.down, repeat=menu_option_position(2) - menu_option_position(1))
        player1_animation.append_steps(Direction.left, Direction.down)
        player1_animation.append_step(Direction.right, repeat=MENU_OPTION_WIDTH + 4)

        # Player 2 push down
        player2_animation.append_step(Direction.right, repeat=MENU_OPTION_RIGHT)
        player2_animation.append_step(Direction.down)
        # Player 2 wait
        player2_animation.append_still(repeat=len(player1_animation.steps) - len(player2_animation.steps))
        player2_animation.append_step(Direction.down, repeat=menu_option_position(4) - menu_option_position(3))

        self.player1_animation_player = player1_animation.create_player()
        self.player2_animation_player = player2_animation.create_player()

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


class OptionsView(View[OptionsViewParameters, OptionsViewModel]):
    """
    The options screen that allows the modification of game settings
    """
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

        from views.start_view import StartView, StartViewParameters
        from views.controls_view import ControlsView, ControlsViewParameters

        self.menu_actions: Dict[int, Callable] = {
            0: lambda: self.navigator.go_to_view(ControlsView, ControlsViewParameters()),
            1: lambda: self.navigator.go_to_view(StartView, StartViewParameters()),
            2: lambda: self.navigator.go_to_view(StartView, StartViewParameters()),
            3: lambda: self.navigator.go_to_view(StartView, StartViewParameters())
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
        from views.start_view import StartView, StartViewParameters

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.menu_actions[self.model.menu_index_selected]()
                    return

                elif event.key == pygame.K_DOWN:
                    self.model.go_down_one_menu_option()

                elif event.key == pygame.K_UP:
                    self.model.go_up_one_menu_option()

                elif event.key == pygame.K_m:
                    self.navigator.go_to_view(StartView, StartViewParameters())

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
                self.model.player1_animation_player.reset()
                self.model.player2_animation_player.reset()
                self.position_start_time = time()
        elif self.position_start_time:
            now = time()
            if now - self.position_start_time >= START_WAIT_SECONDS:
                self.position_start_time = None
        elif self.model.player1_animation_player.is_finished and self.model.player2_animation_player.is_finished:
            self.position_won_time = time()
        else:
            # Next position for the player...
            if not self.model.player1_animation_player.is_finished:
                self.model.player1_piece.move(self.model.player1_animation_player.play_next_step())
            if not self.model.player2_animation_player.is_finished:
                self.model.player2_piece.move(self.model.player2_animation_player.play_next_step())

    def draw_animated(self):
        self.menu_view.draw_animated()
