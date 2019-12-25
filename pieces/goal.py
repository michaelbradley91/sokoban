from typing import Tuple

import pygame

from colours import RED
from pieces.piece import Piece
from resources import scale


class GoalPiece(Piece):
    """
    A piece representing a goal, which is where a crate needs to be pushed to.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Goals should never need to move, and allow anything on top of them
        """
        return True

    def draw(self, grid_offset: Tuple[int, int], rect: pygame.Rect):
        self.resources.display.blit(scale(rect, self.resources.goal_image), rect)
