from time import time
import pygame
from pygame.rect import Rect

from animator import Animator, Animation
from colours import YELLOW, BLACK
from coordinate import Coordinate
from direction import Direction
from grid import Grid
from pieces.piece import Piece
from resources import Resources, scale
from undo import UndoManager


# Seconds per square
WALK_SPEED = 0.3
# Animation speed in milliseconds
ANIMATION_SPEED = 100


class PlayerPiece(Piece):
    """
    A piece representing a player!
    """
    def __init__(self, grid: Grid, undo_manager: UndoManager, animator: Animator, resources: Resources):
        super().__init__(grid, undo_manager, animator, resources)
        self.direction = Direction.left
        self.animation_start = 0
        self.animation_percentage = 0
        self.animation_phase = 0

    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Nothing is allowed to actually move the player
        """
        return False

    def move(self, coordinate: Coordinate):
        def set_direction(direction: Direction):
            self.direction = direction

        coordinate_change = coordinate - self.coordinate

        old_direction = self.direction
        if coordinate_change.x > 0:
            self.direction = Direction.right
        if coordinate_change.x < 0:
            self.direction = Direction.left
        if coordinate_change.y > 0:
            self.direction = Direction.down
        if coordinate_change.y < 0:
            self.direction = Direction.up
        new_direction = self.direction

        if new_direction != old_direction:
            self.undo_manager.register(lambda: set_direction(old_direction), lambda: set_direction(new_direction))

        if not super().move(coordinate):
            return False

        animation = Animation(self.check_animation, self.cancel_animation)
        self.animator.add_animation(animation)
        self.animation_start = time()
        self.animation_percentage = 0
        self.animation_phase = 0

        return True

    def check_animation(self):
        now = time()
        if now - self.animation_start >= WALK_SPEED:
            self.animation_start = 0
            return True
        self.animation_percentage = (now - self.animation_start) / WALK_SPEED
        self.animation_phase = int(((now - self.animation_start) * 1000) / ANIMATION_SPEED) % 3
        return False

    def cancel_animation(self):
        self.animation_start = 0
        self.animation_percentage = 0
        self.animation_phase = 0

    def draw(self, rect: pygame.Rect):
        if not self.animation_start:
            image = self.resources.get_player_image(self.direction, 0)
            self.resources.display.blit(scale(rect, image), rect)
            return

        # Draw at the partial location
        if self.direction in [Direction.left, Direction.right]:
            x_distance = (1 - self.animation_percentage) * rect.width * (1 if self.direction == Direction.left else -1)
            y_distance = 0
        else:
            y_distance = (1 - self.animation_percentage) * rect.height * (1 if self.direction == Direction.up else -1)
            x_distance = 0

        new_rect = Rect(int(rect.x + x_distance),
                        int(rect.y + y_distance),
                        int(rect.width),
                        int(rect.height))
        image = self.resources.get_player_image(self.direction, self.animation_phase)
        self.resources.display.blit(scale(new_rect, image), new_rect)
