from typing import TYPE_CHECKING
from typing import Tuple

from app_container import AppContainer
from opengl_support.drawable import Drawable
from pieces.piece import Piece

if TYPE_CHECKING:
    from grid import Grid


class StaticPiece(Piece):
    def __init__(self, grid: "Grid", app_container: AppContainer, drawable: Drawable, allow_player_move: bool = False):
        super().__init__(grid, app_container)
        self.drawable = drawable
        self.allow_player_move = allow_player_move

    def react_to_piece_move(self, piece: "Piece") -> bool:
        return self.allow_player_move

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.drawable.draw(self.get_rect_at_coordinate(grid_offset, square_size))
