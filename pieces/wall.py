from typing import Tuple

import pygame

from colours import GREY
from pieces.piece import Piece
from resources import scale, dim


class WallPiece(Piece):
    """
    A piece representing a simple wall.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        return False

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.draw_at_coordinate(grid_offset, square_size, self.coordinate, self.resources.wall_image)
