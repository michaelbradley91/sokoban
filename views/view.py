from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from animator import Animator
from music_player import MusicPlayer
from resources import Resources
from undo import UndoManager

T = TypeVar('T')


class View(ABC, Generic[T]):
    def __init__(self, undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer, resources: Resources):
        self.view_data = Optional[T] = None
        self.undo_manager = undo_manager
        self.animator = animator
        self.music_player = music_player
        self.resources = resources

    def initialise(self, view_data: T):
        """ Initialise the view by saving the view data and resetting various resources """
        self.view_data = view_data

        self.undo_manager.reset()
        self.animator.reset()
        self.music_player.reset()

        self.init()

    @abstractmethod
    def init(self):
        """ View specific initialisation """
        pass
