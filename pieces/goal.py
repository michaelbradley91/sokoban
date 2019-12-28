from typing import Tuple

from pieces.piece import Piece


class GoalPiece(Piece):
    """
    A piece representing a goal, which is where a crate needs to be pushed to.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Goals should never need to move, and allow anything on top of them
        """
        return True

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.resources.goal.draw(self.get_rect_at_coordinate(grid_offset, square_size))
