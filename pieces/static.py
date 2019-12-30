from typing import Tuple

from animator import Animator
from music_player import MusicPlayer
from opengl_support.drawable import Drawable
from pieces.piece import Piece
from resources import Resources
from undo import UndoManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid


class StaticPiece(Piece):
    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer,
                 resources: Resources, drawable: Drawable, allow_player_move: bool = False):
        super().__init__(grid, undo_manager, animator, music_player, resources)
        self.drawable = drawable
        self.allow_player_move = allow_player_move

    def react_to_piece_move(self, piece: "Piece") -> bool:
        return self.allow_player_move

    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        self.drawable.draw(self.get_rect_at_coordinate(grid_offset, square_size))
