from typing import Tuple, Optional

from animations.linear_animation import LinearAnimation
from app_container import AppContainer
from constants.direction import coordinate_change_to_direction
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
        self.was_moving_previously = False

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

        old_direction = None
        new_direction = 1
        if self.was_moving_previously:
            old_direction = coordinate_change_to_direction(
                self.animation.finish_position - self.animation.start_position)
            new_direction = coordinate_change_to_direction(coordinate - old_coordinate)

        if self.was_moving_previously and old_direction == new_direction:
            # Reuse the previous animation
            new_finish = self.animation.finish_position + (coordinate - old_coordinate)
            self.animation.travel_time += WALK_SPEED
            old_start_time = self.animation.start_time
            self.animation.finish_position = new_finish
            self.animation.un_finish()
            self.animator.add_animation(self.animation)
            self.animation.start_time = old_start_time
        else:
            self.animation = CrateAnimation(old_coordinate, coordinate)
            self.animator.add_animation(self.animation)

        if any(p for p in self.grid[self.coordinate] if type(p) == GoalPiece):
            self.music_player.play_crate_moved_onto_goal()
        else:
            self.music_player.play_crate_slide()
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.was_moving_previously = False
            self.resources.crate.draw(self.get_rect_at_coordinate(grid_offset, square_size))
        else:
            self.was_moving_previously = True
            animation_status = self.animation.calculate(grid_offset, square_size)
            self.resources.crate.draw(animation_status.rect)
