from typing import Optional, Tuple, Callable

from animations.animation import Animation
from animations.linear_animation import LinearAnimation
from animations.static_animation import StaticAnimation
from app_container import AppContainer
from constants.direction import Direction, coordinate_change_to_direction
from coordinate import Coordinate
from grid import Grid
from pieces.piece import Piece

# Seconds per square in milliseconds
WALK_SPEED = 300
# Animation speed in milliseconds
ANIMATION_SPEED = 100


class PlayerAnimation(LinearAnimation):
    def __init__(self, number_of_images: int, start: Coordinate, finish: Coordinate,
                 finished: Callable[[LinearAnimation], None]):
        super().__init__(start.to_float(), finish.to_float(), number_of_images, WALK_SPEED, ANIMATION_SPEED, finished)


class PlayerPiece(Piece):
    """
    A piece representing a player!
    """

    def __init__(self, grid: "Grid", app_container: AppContainer):
        super().__init__(grid, app_container)
        self.direction = Direction.left
        self.animation: Optional[Animation] = None

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

        self.animation = PlayerAnimation(len(self.resources.player[self.direction]), old_coordinate, coordinate, lambda _: None)
        self.animator.add_animation(self.animation)

        return True

    def run_on_the_spot(self):
        self.animation = StaticAnimation(len(self.resources.player[self.direction]), ANIMATION_SPEED)
        self.animator.add_animation(self.animation)

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.resources.player[self.direction][0].draw(self.get_rect_at_coordinate(grid_offset, square_size))
        elif isinstance(self.animation, PlayerAnimation):
            animation_status = self.animation.calculate(grid_offset, square_size)
            self.resources.player[self.direction][animation_status.image_index].draw(animation_status.rect)
        elif isinstance(self.animation, StaticAnimation):
            rect = self.get_rect_at_coordinate(grid_offset, square_size)
            self.resources.player[self.direction][self.animation.image_index].draw(rect)
        else:
            raise ValueError("Unknown animation type")
