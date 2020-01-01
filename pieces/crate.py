from typing import Tuple, Optional, Callable

from constants.direction import coordinate_change_to_direction, try_get_move_from_key, Direction
from animations.linear_animation import LinearAnimation
from app_container import AppContainer
from coordinate import Coordinate
from grid import Grid
from pieces.goal import GoalPiece
from pieces.piece import Piece
from pieces.player import WALK_SPEED


class CrateAnimation(LinearAnimation):
    def __init__(self, start: Coordinate, finish: Coordinate):
        super().__init__(start, finish, 1, WALK_SPEED, 1)


class CratePiece(Piece):
    """
    A piece representing a crate, which needs to be pushed onto a goal.
    """

    def __init__(self, grid: "Grid", app_container: AppContainer):
        super().__init__(grid, app_container)
        self.animation: Optional[CrateAnimation] = None
        self.animation_direction: Optional[Direction] = None

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

        direction_change = coordinate_change_to_direction(self.coordinate - old_coordinate)
        if self.animation and self.animation_direction == direction_change:
            self.animation.extend(1, WALK_SPEED)
        else:
            self.animation_direction = direction_change
            self.animation = CrateAnimation(old_coordinate, coordinate)
        self.animator.add_animation(self.animation)

        if any(p for p in self.grid[self.coordinate] if type(p) == GoalPiece):
            self.music_player.play_crate_moved_onto_goal()
        else:
            self.music_player.play_crate_slide()
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.animation = None
            self.animation_direction = None
            self.resources.crate.draw(self.get_rect_at_coordinate(grid_offset, square_size))
        else:
            animation_status = self.animation.calculate(grid_offset, square_size)
            self.resources.crate.draw(animation_status.rect)
