from typing import Tuple, Optional

from animations.linear_animation import LinearAnimation
from animator import Animator
from coordinate import Coordinate
from drawer import Drawer
from grid import Grid
from music_player import MusicPlayer
from pieces.goal import GoalPiece
from pieces.piece import Piece
from pieces.player import WALK_SPEED
from resources import Resources
from undo import UndoManager


class CrateAnimation(LinearAnimation):
    def __init__(self, start: Coordinate, finish: Coordinate):
        super().__init__(start, finish, 1, WALK_SPEED, 1)


class CratePiece(Piece):
    """
    A piece representing a crate, which needs to be pushed onto a goal.
    """

    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator,
                 drawer: Drawer, music_player: MusicPlayer, resources: Resources):
        super().__init__(grid, undo_manager, animator, drawer, music_player, resources)
        self.animation: Optional[CrateAnimation] = None

    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Only allow the player to move crates, and only one crate at a time.
        """
        piece_coordinate = self.grid.get_piece_coordinate(piece)
        coordinate_change = self.coordinate - piece_coordinate
        new_coordinate = self.coordinate + coordinate_change

        return self.move(new_coordinate)

    def move(self, coordinate: Coordinate):
        old_coordinate = self.coordinate
        if not super().move(coordinate):
            return False

        self.animation = CrateAnimation(old_coordinate, coordinate)
        self.animator.add_animation(self.animation)

        if any(p for p in self.grid[self.coordinate] if type(p) == GoalPiece):
            self.music_player.play_crate_moved_onto_goal()
        else:
            self.music_player.play_crate_slide()
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.drawer.draw_crate(self.get_rect_at_coordinate(grid_offset, square_size))
        else:
            self.animation.draw(lambda r, i: self.drawer.draw_crate(r), grid_offset, square_size)
