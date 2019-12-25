from time import time
from typing import Tuple, Optional

import pygame
from pygame.rect import Rect

from LinearAnimation import LinearAnimation
from animator import Animator, Animation
from colours import  GREEN
from coordinate import Coordinate
from direction import Direction
from grid import Grid
from pieces.goal import GoalPiece
from pieces.piece import Piece
from pieces.player import PlayerPiece, WALK_SPEED
from resources import scale, Resources
from undo import UndoManager


class CrateAnimation(LinearAnimation):
    def __init__(self, resources: Resources, start: Coordinate, finish: Coordinate):
        super().__init__(start, finish, [resources.crate_image], WALK_SPEED, 1)


class CratePiece(Piece):
    """
    A piece representing a crate, which needs to be pushed onto a goal.
    """
    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator, resources: Resources):
        super().__init__(grid, undo_manager, animator, resources)
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
        coordinate_change = coordinate - self.coordinate
        if not super().move(coordinate):
            return False

        if coordinate_change.x > 0:
            self.animation_direction = Direction.right
        if coordinate_change.x < 0:
            self.animation_direction = Direction.left
        if coordinate_change.y > 0:
            self.animation_direction = Direction.down
        if coordinate_change.y < 0:
            self.animation_direction = Direction.up

        self.animation = CrateAnimation(self.resources, old_coordinate, coordinate)
        self.animator.add_animation(self.animation)

        if any(p for p in self.grid[self.coordinate] if type(p) == GoalPiece):
            self.resources.music_player.play_crate_moved_onto_goal()
        else:
            self.resources.music_player.play_crate_slide()
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        if not self.animation or self.animation.is_finished:
            self.draw_at_coordinate(grid_offset, square_size, self.coordinate, self.resources.crate_image)
        else:
            self.animation.draw(self.resources.display, grid_offset, square_size)

