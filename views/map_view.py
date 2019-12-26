import pygame
from typing import List, NamedTuple, Tuple

from pygame.event import EventType

from colours import BLACK
from direction import Direction, direction_sorter, direction_to_coordinate, try_get_move_from_key
from map_reader import read_map
from maps.maps import MAPS
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from views.view import View, ViewModel


PLAYER_MOVE_UNDO_LABEL = "player_move"


class MapViewParameters(NamedTuple):
    map_index: int


class MapViewModel(ViewModel[MapViewParameters]):
    def __init__(self, view: "MapView"):
        super().__init__(view)

        map_definition = MAPS[self.parameters.map_index]

        self.undo_manager.enabled = False
        self.grid = read_map(self.undo_manager, self.resources, self.animator, self.music_player, map_definition)
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
    def init(self):
        pass

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

            if 0 <= map_index < len(MAPS):
                self.navigator.go_to_view(MapView, MapViewParameters(map_index=map_index))
                return False

            # Only allow one key to be processed at once
            return False

    def draw(self):
        self.resources.display.fill(BLACK)

        for piece_type in PIECE_DRAW_ORDER:
            for piece in self.grid.get_pieces_of_type(piece_type):
                piece.draw(self.grid_offset, self.grid_square_size)

        if self.model.map_won:
            self.draw_you_win()

    def draw_you_win(self):
        """
        Draw the you win text!
        :return: nothing
        """
        you_win: pygame.SurfaceType = self.resources.you_win_font.render("You win!", True, pygame.Color('black'))

        target_height = int(self.grid_square_size / 1.5)
        target_width = int((you_win.get_width() / you_win.get_height()) * target_height)

        you_win = pygame.transform.scale(you_win, (target_width, target_height))

        centre = self.resources.display.get_width() / 2, self.resources.display.get_height() / 2
        x = centre[0] - (you_win.get_width() // 2)
        y_centre = self.grid_offset[1] + (((self.grid.height - 1) // 2) * self.grid_square_size) + (
                    self.grid_square_size // 2)
        y = y_centre - (you_win.get_height() // 2)

        self.resources.display.blit(you_win, (x, y))

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

    def close(self):
        pass

    @property
    def grid_size(self) -> Tuple[int, int]:
        return self.grid_square_size * self.grid.width, self.grid_square_size * self.grid.height

    @property
    def grid_offset(self) -> Tuple[int, int]:
        x_offset = (self.resources.display.get_width() - (self.grid_square_size * self.grid.width)) // 2
        y_offset = (self.resources.display.get_height() - (self.grid_square_size * self.grid.height)) // 2
        return x_offset, y_offset

    @property
    def grid_square_size(self) -> int:
        return min(self.resources.display.get_width() // self.grid.width,
                   self.resources.display.get_height() // self.grid.height)

    @property
    def grid(self):
        return self.model.grid
