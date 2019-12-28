from typing import Tuple

from pieces.piece import Piece


class WallPiece(Piece):
    """
    A piece representing a simple wall.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        return False

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.resources.wall.draw(self.get_rect_at_coordinate(grid_offset, square_size))
