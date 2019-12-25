from typing import Optional, Tuple, List

import pygame

from animator import Animator
from colours import BLACK
from coordinate import Coordinate
from pygame.event import EventType
from pygame.font import Font, SysFont
from pygame.rect import Rect
from pygame.time import Clock

from direction import Direction, direction_sorter, direction_to_coordinate, try_get_move_from_key
from grid import Grid
from map_reader import read_map
from maps.maps import MAPS
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.piece_draw_order import PIECE_DRAW_ORDER
from pieces.player import PlayerPiece
from resources import Resources
from undo import UndoManager


class App:
    def __init__(self):
        self._running = True
        self.map_won = False
        self.size = self.width, self.height = 640, 704
        self.resources: Optional[Resources] = None
        self.undo_manager = UndoManager()
        self.animator = Animator(self.undo_manager)
        self.grid: Optional[Grid] = None
        self.clock = Clock()

    @property
    def players_can_move(self):
        return not self.map_won and not self.animator.animating()

    def on_init(self):
        pygame.mixer.init(buffer=128)
        pygame.init()
        pygame.mixer.music.load("resources/Puzzle-Dreams-3.mp3")
        pygame.mixer.music.play(-1)

        display = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        self._running = True

        self.resources = Resources(display)
        self.init_map(MAPS[0])
        return True

    def init_map(self, map: List[List[str]]):
        self.map_won = False
        self.undo_manager = UndoManager()
        self.animator = Animator(self.undo_manager)
        self.undo_manager.enabled = False
        self.grid = read_map(self.undo_manager, self.resources, self.animator, map)
        self.undo_manager.enabled = True
        self.undo_manager.save_position("player_move")

    def on_event(self, event: EventType):
        if event.type == pygame.QUIT:
            self._running = False

        # Handle screen resizing
        if event.type == pygame.VIDEORESIZE:
            self.size = self.width, self.height = event.w, event.h
            self.resources.display = pygame.display.set_mode(self.size, self.resources.display.get_flags())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._running = False

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

            if 0 <= map_index < len(MAPS):
                self.init_map(MAPS[map_index])

            # Move the player only if no animations are running
            if self.players_can_move:
                if event.key == pygame.K_u:
                    self.undo_manager.undo("player_move")
                if event.key == pygame.K_r:
                    self.undo_manager.redo("player_move")
                if event.key == pygame.K_f:
                    flags = self.resources.display.get_flags()
                    new_flags = flags ^ pygame.FULLSCREEN
                    self.resources.display = pygame.display.set_mode(self.size, new_flags)

    def pre_event_loop(self):
        self.animator.run_animations()

    def post_event_loop(self):
        if self.players_can_move:
            pressed_keys = pygame.key.get_pressed()
            move = try_get_move_from_key(pressed_keys)
            if move:
                self.move_players(move)

        if not self.map_won:
            self.check_win()

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
    def grid_size(self) -> Tuple[int ,int]:
        return self.square_size * self.grid.width, self.square_size * self.grid.height

    @property
    def grid_offset(self) -> Tuple[int, int]:
        x_offset = (self.resources.display.get_width() - (self.square_size * self.grid.width)) // 2
        y_offset = (self.resources.display.get_height() - (self.square_size * self.grid.height)) // 2
        return x_offset, y_offset

    @property
    def square_size(self) -> int:
        return min(self.resources.display.get_width() // self.grid.width,
                   self.resources.display.get_height() // self.grid.height)

    def on_render(self):
        self.resources.display.fill(BLACK)

        for piece_type in PIECE_DRAW_ORDER:
            for piece in self.grid.get_pieces_of_type(piece_type):
                rect = Rect(self.grid_offset[0] + self.square_size * piece.coordinate.x,
                            self.grid_offset[1] + self.square_size * piece.coordinate.y,
                            self.square_size,
                            self.square_size)
                piece.draw(rect)

        if self.map_won:
            you_win: pygame.SurfaceType = self.resources.you_win_font.render("You win!", True, pygame.Color('black'))
            target_height = int(self.square_size / 1.5)
            target_width = int((you_win.get_width() / you_win.get_height()) * target_height)
            you_win = pygame.transform.scale(you_win, (target_width, target_height))

            centre = self.resources.display.get_width() / 2, self.resources.display.get_height() / 2
            x = centre[0] - (you_win.get_width() // 2)
            y_centre = self.grid_offset[1] + ((self.grid.height // 2) * self.square_size) + (self.square_size // 2)
            y = y_centre - (you_win.get_height() // 2)
            self.resources.display.blit(you_win, (x, y))

        pygame.display.update()

    def check_win(self):
        self.map_won = True
        for crate in self.grid.get_pieces_of_type(CratePiece):
            if not any([p for p in self.grid[crate.coordinate] if type(p) == GoalPiece]):
                self.map_won = False
        if self.map_won:
            pygame.mixer.Channel(1).play(self.resources.win_sound)

    def on_clean_up(self):
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = False

        while self._running:
            self.pre_event_loop()
            for event in pygame.event.get():
                self.on_event(event)
            self.post_event_loop()
            self.on_render()
            self.clock.tick(60)
        self.on_clean_up()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
