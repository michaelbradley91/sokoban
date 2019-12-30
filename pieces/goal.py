from animator import Animator
from grid import Grid
from music_player import MusicPlayer
from pieces.static import StaticPiece
from resources import Resources
from undo import UndoManager


class GoalPiece(StaticPiece):
    """
    A piece representing a goal, which is where a crate needs to be pushed to.
    """

    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer,
                 resources: Resources):
        super().__init__(grid, undo_manager, animator, music_player, resources, resources.goal, True)
