from typing import Tuple

from pieces.piece import Piece


class NothingPiece(Piece):
    """
    A piece representing nothing.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Allows anything to be moved on top of it.
        """
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.resources.floor.draw(self.get_rect_at_coordinate(grid_offset, square_size))
