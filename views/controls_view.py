from enum import Enum
from typing import List

from pygame.event import EventType

from app_container import AppContainer
from constants.colours import BACKGROUND_COLOUR
from coordinate import Coordinate
from layouts.layout import BasicLayout
from opengl_support.helpers import set_background_and_clear
from views.components.menu_text_item_view import MenuTextItemViewModel, MenuTextItemView
from views.components.menu_view import MenuViewModel, MenuView
from views.components.title_view import TITLE_HEIGHT
from views.view import ViewModel, View
from constants.text import CONTROLS_VIEW_MAIN_MENU, CONTROLS_VIEW_QUIT, CONTROLS_VIEW_DOWN, CONTROLS_VIEW_FULLSCREEN, \
    CONTROLS_VIEW_LEFT, CONTROLS_VIEW_MOVEMENT, CONTROLS_VIEW_RIGHT, CONTROLS_VIEW_SHORTCUTS, CONTROLS_VIEW_UP, \
    CONTROLS_VIEW_BACK_TO_MAIN_MENU

GRID_WIDTH = 17
GRID_HEIGHT = TITLE_HEIGHT + 2 + (2 * 5) + 1


class MenuOption(Enum):
    up = CONTROLS_VIEW_UP
    down = CONTROLS_VIEW_DOWN
    left = CONTROLS_VIEW_LEFT
    right = CONTROLS_VIEW_RIGHT
    fullscreen = CONTROLS_VIEW_FULLSCREEN
    main_menu = CONTROLS_VIEW_MAIN_MENU
    quit = CONTROLS_VIEW_QUIT


MOVEMENT_MENU_OPTIONS = [MenuOption.up, MenuOption.down, MenuOption.left, MenuOption.right]
SHORTCUTS_MENU_OPTIONS = [MenuOption.fullscreen, MenuOption.main_menu, MenuOption.quit]
MOVEMENT_MENU_OPTION_WIDTH = 2
SHORTCUTS_MENU_OPTION_WIDTH = 4
MOVEMENT_MENU_OPTION_BY_INDEX = {i: m for i, m in enumerate(MOVEMENT_MENU_OPTIONS)}
MOVEMENT_INDEX_BY_MENU_OPTION = {m: i for i, m in enumerate(MOVEMENT_MENU_OPTIONS)}
SHORTCUTS_MENU_OPTON_BY_INDEX = {i: m for i, m in enumerate(SHORTCUTS_MENU_OPTIONS)}
SHORTCUTS_INDEX_BY_MENU_OPTION = {m: i for i, m in enumerate(SHORTCUTS_MENU_OPTIONS)}

CONTROLS_MENU_START_POSITION = "start_position"


def menu_left_position(m: MenuOption):
    if m in MOVEMENT_MENU_OPTIONS:
        return 2
    else:
        return 8


def menu_right_position(m: MenuOption):
    left = menu_left_position(m)
    if m in MOVEMENT_MENU_OPTIONS:
        return left + MOVEMENT_MENU_OPTION_WIDTH
    else:
        return left + SHORTCUTS_MENU_OPTION_WIDTH


def menu_y_position(m: MenuOption):
    if m in MOVEMENT_MENU_OPTIONS:
        return 1 + TITLE_HEIGHT + 1 + 2 + (MOVEMENT_INDEX_BY_MENU_OPTION[m] * 2)
    else:
        return 1 + TITLE_HEIGHT + 1 + 2 + (SHORTCUTS_INDEX_BY_MENU_OPTION[m] * 2)


class ControlsViewParameters:
    pass


class ControlsViewModel(ViewModel[ControlsViewParameters]):
    def __init__(self, view: "ControlsView"):
        super().__init__(view)
        self.resources.crate_sound.set_volume(0)

        self.undo_manager.enabled = False
        self.menu_view_model = MenuViewModel(self.app_container, GRID_WIDTH, GRID_HEIGHT)

        # Add menu options
        for m in MOVEMENT_MENU_OPTIONS + SHORTCUTS_MENU_OPTIONS:
            x = menu_left_position(m)
            width = menu_right_position(m) - x
            y = menu_y_position(m)
            menu_item_view_model = MenuTextItemViewModel(self.app_container, self.menu_view_model.grid,
                                                         Coordinate(x, y), column_span=width)
            self.menu_view_model.add_menu_item(menu_item_view_model)

        # Add the titles. These are like un-selectable menu options
        x = menu_left_position(MOVEMENT_MENU_OPTIONS[0])
        y = 1 + TITLE_HEIGHT + 1
        menu_item_view_model = MenuTextItemViewModel(self.app_container, self.menu_view_model.grid,
                                                     Coordinate(x, y), column_span=4)
        self.menu_view_model.add_menu_item(menu_item_view_model)
        x = menu_left_position(SHORTCUTS_MENU_OPTIONS[0])
        menu_item_view_model = MenuTextItemViewModel(self.app_container, self.menu_view_model.grid,
                                                     Coordinate(x, y), column_span=6)
        self.menu_view_model.add_menu_item(menu_item_view_model)

        self.menu_selected: MenuOption = MenuOption.up
        self.get_menu_text_item(self.menu_selected).highlighted = True

        self.load_grid()
        self.undo_manager.enabled = True

    def load_grid(self):
        """ Load the structure of the grid. This is a bit complicated... """

    def get_menu_text_item(self, menu_option: MenuOption) -> MenuTextItemViewModel:
        """ Get the menu text item view model for the given menu option """
        if menu_option in MOVEMENT_MENU_OPTIONS:
            index = MOVEMENT_INDEX_BY_MENU_OPTION[menu_option]
        else:
            index = len(MOVEMENT_MENU_OPTIONS) + SHORTCUTS_INDEX_BY_MENU_OPTION[menu_option]
        return self.menu_view_model.menu_items[index]

    @property
    def movement_title(self) -> MenuTextItemViewModel:
        return self.menu_view_model.menu_items[len(MOVEMENT_MENU_OPTIONS) + len(SHORTCUTS_MENU_OPTIONS)]

    @property
    def shortcuts_title(self) -> MenuTextItemViewModel:
        return self.menu_view_model.menu_items[len(MOVEMENT_MENU_OPTIONS) + len(SHORTCUTS_MENU_OPTIONS) + 1]


class ControlsView(View[ControlsViewParameters, ControlsViewModel]):
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

    def init(self):
        menu_container_layout = BasicLayout()
        self.menu_view = MenuView(self.app_container, self.model.menu_view_model, menu_container_layout)

        # Add menu items
        for m in MenuOption:
            model = self.model.get_menu_text_item(m)
            menu_item_view = MenuTextItemView(self.app_container, model, self.menu_view.grid_layout, m.value)
            self.menu_view.menu_items.append(menu_item_view)

        menu_item_view = MenuTextItemView(self.app_container, self.model.movement_title, self.menu_view.grid_layout,
                                          CONTROLS_VIEW_MOVEMENT)
        self.menu_view.menu_items.append(menu_item_view)
        menu_item_view = MenuTextItemView(self.app_container, self.model.shortcuts_title, self.menu_view.grid_layout,
                                          CONTROLS_VIEW_SHORTCUTS)
        self.menu_view.menu_items.append(menu_item_view)

        self.layout.set_layout(menu_container_layout)
        self.resources.crate_sound.set_volume(0)

        self.undo_manager.save_position(CONTROLS_MENU_START_POSITION)

    def close(self):
        pass

    def pre_event_loop(self):
        pass

    def on_events(self, events: List[EventType]):
        pass

    def post_event_loop(self):
        pass

    def draw_static(self):
        set_background_and_clear(BACKGROUND_COLOUR)
        self.menu_view.draw_static()

    def post_animation_loop(self):
        pass

    def draw_animated(self):
        self.menu_view.draw_animated()
