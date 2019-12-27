from typing import Optional, Tuple

from LinearAnimation import LinearAnimation
from animator import Animator
from coordinate import Coordinate
from direction import Direction, coordinate_change_to_direction
from drawer import Drawer
from grid import Grid
from music_player import MusicPlayer
from pieces.piece import Piece
from resources import Resources
from undo import UndoManager

# Seconds per square in milliseconds
WALK_SPEED = 300
# Animation speed in milliseconds
ANIMATION_SPEED = 100


class PlayerAnimation(LinearAnimation):
    def __init__(self, drawer: Drawer, start: Coordinate, finish: Coordinate):
        super().__init__(start, finish, drawer.number_of_player_phases(), WALK_SPEED, ANIMATION_SPEED)


class PlayerPiece(Piece):
    """
    A piece representing a player!
    """

    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator,
                 drawer: Drawer, music_player: MusicPlayer, resources: Resources):
        super().__init__(grid, undo_manager, animator, drawer, music_player, resources)
        self.direction = Direction.left
        self.animation: Optional[PlayerAnimation] = None

    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Nothing is allowed to actually move the player
        """
        return False

    def move(self, coordinate: Coordinate):
        def set_direction(direction: Direction):
            self.direction = direction

        old_coordinate = self.coordinate
        coordinate_change = coordinate - self.coordinate

        old_direction = self.direction
        self.direction = coordinate_change_to_direction(coordinate_change)
        new_direction = self.direction

        if new_direction != old_direction:
            self.undo_manager.register(lambda: set_direction(old_direction), lambda: set_direction(new_direction))

        if not super().move(coordinate):
            return False

        self.animation = PlayerAnimation(self.drawer, old_coordinate, coordinate)
        self.animator.add_animation(self.animation)

        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.drawer.draw_player(self.get_rect_at_coordinate(grid_offset, square_size), self.direction, 0)
        else:
            self.animation.draw(lambda r, i: self.drawer.draw_player(r, self.direction, i), grid_offset, square_size)
