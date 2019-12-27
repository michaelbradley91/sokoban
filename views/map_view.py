from typing import List, NamedTuple, Optional

import pygame
from pygame.event import EventType

from animator import Animator
from colours import BLACK
from coordinate import Coordinate
from direction import Direction, direction_sorter, direction_to_coordinate, try_get_move_from_key
from drawer import Drawer
from layouts.aspect_layout import AspectLayout
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from layouts.margin_layout import MarginLayout
from map_reader import read_map
from maps.maps import MAPS
from music_player import MusicPlayer
from navigator import Navigator
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from resources import Resources
from undo import UndoManager
from views.view import View, ViewModel


BACKGROUND_COLOUR = pygame.Color("black")
PLAYER_MOVE_UNDO_LABEL = "player_move"
YOU_WIN_TEXT = "You win!"
YOU_WIN_COLOUR = pygame.Color("black")


class MapViewParameters(NamedTuple):
    map_index: int


class MapViewModel(ViewModel[MapViewParameters]):
    def __init__(self, view: "MapView"):
        super().__init__(view)

        map_definition = MAPS[self.parameters.map_index]

        self.undo_manager.enabled = False
        self.grid = read_map(self.undo_manager, self.resources, self.animator, self.drawer,
                             self.music_player, map_definition)
        self.undo_manager.enabled = True
        self.undo_manager.save_position(PLAYER_MOVE_UNDO_LABEL)
        self.map_won = False

    @property
    def players_can_move(self):
        return not self.map_won and not self.animator.animating()

    def check_win(self):
        self.map_won = True
        for crate in self.grid.get_pieces_of_type(CratePiece):
            if not any([p for p in self.grid[crate.coordinate] if type(p) == GoalPiece]):
                self.map_won = False
        if self.map_won:
            self.music_player.play_you_win()


class MapView(View[MapViewParameters, MapViewModel]):
    """
    A map view.
    """
    def __init__(self, undo_manager: UndoManager, animator: Animator, drawer: Drawer, music_player: MusicPlayer,
                 resources: Resources, navigator: Navigator, layout: BasicLayout):

        super().__init__(undo_manager, animator, drawer, music_player, resources, navigator, layout)
        self.grid_layout: Optional[GridLayout] = None
        self.square_layout: Optional[BasicLayout] = None
        self.you_win_layout: Optional[BasicLayout] = None
        self.you_win: Optional[pygame.SurfaceType] = None

    def init(self):
        # Build the layout for the page
        self.square_layout = BasicLayout()
        self.you_win_layout = BasicLayout()

        you_win_surface = self.resources.you_win_font.get_surface(YOU_WIN_TEXT, YOU_WIN_COLOUR)

        aspect_layout = AspectLayout(you_win_surface.get_size())
        aspect_layout.set_layout(self.you_win_layout)

        margin_layout = MarginLayout((0, 1 / 5))
        margin_layout.set_layout(aspect_layout)

        self.grid_layout = GridLayout(width=self.grid.width, height=self.grid.height)
        self.grid_layout.add_layout(self.square_layout, Coordinate(0, 0))
        self.grid_layout.add_layout(margin_layout, Coordinate(0, self.grid.height // 2),
                                    column_span=self.grid.width)

        aspect_layout = AspectLayout((self.grid.width, self.grid.height), (self.grid.width, self.grid.height))
        aspect_layout.set_layout(self.grid_layout)

        self.layout.set_layout(aspect_layout)

    def pre_event_loop(self):
        pass

    def post_event_loop(self):
        if self.model.players_can_move:
            pressed_keys = pygame.key.get_pressed()
            move = try_get_move_from_key(pressed_keys)
            if move:
                self.move_players(move)

        if not self.model.map_won:
            self.model.check_win()

    def on_events(self, events: List[EventType]):
        for event in events:
            if not self.on_event(event):
                return

    def on_event(self, event: EventType):
        if event.type == pygame.KEYDOWN:
            if self.model.players_can_move:
                if event.key == pygame.K_u:
                    self.undo_manager.undo(PLAYER_MOVE_UNDO_LABEL)
                if event.key == pygame.K_r:
                    self.undo_manager.redo(PLAYER_MOVE_UNDO_LABEL)

            # Patch to allow changing levels without a level menu!
            map_index = -1
            if event.key == pygame.K_1:
                map_index = 0
            if event.key == pygame.K_2:
                map_index = 1
            if event.key == pygame.K_3:
                map_index = 2
            if event.key == pygame.K_4:
                map_index = 3
            if event.key == pygame.K_5:
                map_index = 4
            if event.key == pygame.K_6:
                map_index = 5
            if event.key == pygame.K_7:
                map_index = 6
            if event.key == pygame.K_8:
                map_index = 7
            if event.key == pygame.K_9:
                map_index = 8
            if event.key == pygame.K_0:
                map_index = 9

            if pygame.key.get_mods() & pygame.KMOD_SHIFT and map_index >= 0:
                map_index += 10

            if pygame.key.get_mods() & pygame.KMOD_ALT and map_index >= 0:
                map_index += 20

            if pygame.key.get_mods() & pygame.KMOD_CTRL and map_index >= 0:
                map_index += 40

            # Go beyond the start screen
            if map_index >= 0:
                map_index += 1

            if 0 <= map_index < len(MAPS):
                self.navigator.go_to_view(MapView, MapViewParameters(map_index=map_index))
                return False

            # Only allow one key to be processed at once
            return False

    def draw(self):
        self.drawer.draw_background(BACKGROUND_COLOUR)

        for piece_type in PIECE_DRAW_ORDER:
            for piece in self.grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_layout.bounding_rect.topleft, self.square_size)

        if self.model.map_won:
            self.draw_you_win()

    def draw_you_win(self):
        """
        Draw the you win text!
        :return: nothing
        """
        self.drawer.draw_you_win(YOU_WIN_TEXT, YOU_WIN_COLOUR, self.you_win_layout.bounding_rect)

    def move_players(self, direction: Direction):
        """
        Move the players.
        :param direction: the direction players should move in
        :return: nothing
        """
        player_moved = False
        players = self.grid.get_pieces_of_type(PlayerPiece)
        players_sorted = sorted(players, key=lambda c: direction_sorter(direction)(c))

        for index, player in enumerate(players_sorted):
            coordinate_change = direction_to_coordinate(direction)
            player_moved = player.move(player.coordinate + coordinate_change) or player_moved

        if player_moved:
            self.undo_manager.save_position("player_move")

    @property
    def square_size(self):
        return self.square_layout.bounding_rect.width

    def close(self):
        pass

    @property
    def grid(self):
        return self.model.grid
