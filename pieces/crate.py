from time import time

import pygame
from pygame.rect import Rect

from animator import Animator
from colours import  GREEN
from coordinate import Coordinate
from direction import Direction
from grid import Grid
from pieces.goal import GoalPiece
from pieces.piece import Piece
from pieces.player import PlayerPiece, WALK_SPEED
from resources import scale, Resources
from undo import UndoManager


class CratePiece(Piece):
    """
    A piece representing a crate, which needs to be pushed onto a goal.
    """
    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator, resources: Resources):
        super().__init__(grid, undo_manager, animator, resources)
        self.animation_direction = Direction.left
        self.animation_start = 0
        self.animation_percentage = 0

    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Only allow the player to move crates, and only one crate at a time.
        """
        piece_coordinate = self.grid.get_piece_coordinate(piece)
        coordinate_change = self.coordinate - piece_coordinate
        new_coordinate = self.coordinate + coordinate_change

        return self.move(new_coordinate)

    def move(self, coordinate: Coordinate):
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

        self.animator.add_animation(self.check_animation)
        self.animation_start = time()
        self.animation_percentage = 0

        if any(p for p in self.grid[self.coordinate] if type(p) == GoalPiece):
            self.resources.crate_success_sound.play()
        else:
            self.resources.crate_sound.play()
        return True

    def check_animation(self):
        now = time()
        if now - self.animation_start >= WALK_SPEED:
            self.animation_start = 0
            return True
        self.animation_percentage = (now - self.animation_start) / WALK_SPEED
        return False

    def draw(self, rect: pygame.Rect):
        image = self.resources.crate_image

        if not self.animation_start:
            self.resources.display.blit(scale(rect, image), rect)
            return

        # Draw at the partial location
        if self.animation_direction in [Direction.left, Direction.right]:
            x_distance = (1 - self.animation_percentage) * rect.width * (1 if self.animation_direction == Direction.left else -1)
            y_distance = 0
        else:
            y_distance = (1 - self.animation_percentage) * rect.height * (1 if self.animation_direction == Direction.up else -1)
            x_distance = 0

        new_rect = Rect(int(rect.x + x_distance),
                        int(rect.y + y_distance),
                        int(rect.width),
                        int(rect.height))
        self.resources.display.blit(scale(new_rect, image), new_rect)
