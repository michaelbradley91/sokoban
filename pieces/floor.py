from animator import Animator
from music_player import MusicPlayer
from pieces.static import StaticPiece
from resources import Resources
from undo import UndoManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grid import Grid


class FloorPiece(StaticPiece):
    """
    A piece representing the floor.
    """

    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer,
                 resources: Resources):
        super().__init__(grid, undo_manager, animator, music_player, resources, resources.floor, True)
