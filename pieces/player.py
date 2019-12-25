from time import time
from typing import Optional, Tuple

import pygame
from pygame.rect import Rect

from LinearAnimation import LinearAnimation
from animator import Animator, Animation
from colours import YELLOW, BLACK
from coordinate import Coordinate
from direction import Direction, coordinate_change_to_direction
from grid import Grid
from pieces.piece import Piece
from resources import Resources, scale
from undo import UndoManager


# Seconds per square in milliseconds
WALK_SPEED = 300
# Animation speed in milliseconds
ANIMATION_SPEED = 100


class PlayerAnimation(LinearAnimation):
    def __init__(self, resources: Resources, start: Coordinate, finish: Coordinate):
        direction = coordinate_change_to_direction(finish - start)
        images = resources.get_player_images(direction)
        super().__init__(start, finish, images, WALK_SPEED, ANIMATION_SPEED)


class PlayerPiece(Piece):
    """
    A piece representing a player!
    """
    def __init__(self, grid: Grid, undo_manager: UndoManager, animator: Animator, resources: Resources):
        super().__init__(grid, undo_manager, animator, resources)
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

        self.animation = PlayerAnimation(self.resources, old_coordinate, coordinate)
        self.animator.add_animation(self.animation)

        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            image = self.resources.get_player_images(self.direction)[0]
            self.draw_at_coordinate(grid_offset, square_size, self.coordinate, image)
        else:
            self.animation.draw(self.resources.display, grid_offset, square_size)
