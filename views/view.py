import pygame
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

from pygame.event import EventType

from animator import Animator
from music_player import MusicPlayer
from resources import Resources
from undo import UndoManager
import typing_inspect

T = TypeVar('T')
S = TypeVar('S')


class View(ABC, Generic[T, S]):
    def __init__(self, undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer, resources: Resources):
        self.parameters: Optional[T] = None
        self.model: Optional[S] = None
        self.undo_manager = undo_manager
        self.animator = animator
        self.music_player = music_player
        self.resources = resources

    def initialise(self, parameters: T):
        """ Initialise the view by saving the parameters and resetting various resources """
        self.parameters = parameters

        self.undo_manager.reset()
        self.animator.reset()
        self.music_player.reset()
        
        self.model: S = type(S)(self)

        self.init()

    @property
    def width(self):
        return self.resources.display.get_width()

    @property
    def height(self):
        return self.resources.display.get_height()

    @abstractmethod
    def init(self):
        """ View specific initialisation """
        pass

    @abstractmethod
    def pre_event_loop(self):
        """ Run some actions before events are processed """
        pass

    @abstractmethod
    def post_event_loop(self):
        """ Run some actions after events have been processed """
        pass

    @abstractmethod
    def on_events(self, events: List[EventType]):
        """ Respond to events """
        pass

    @abstractmethod
    def draw(self):
        """ Draw the view on screen. A top level view like this should occupy the whole screen. """
        pass


class ViewModel(Generic[T]):
    def __init__(self, view: "View[T, ViewModel[T]]"):
        self.view = view

    @property
    def parameters(self) -> T:
        return self.view.parameters

    @property
    def resources(self) -> Resources:
        return self.view.resources

    @property
    def music_player(self) -> MusicPlayer:
        return self.view.music_player

    @property
    def undo_manager(self) -> UndoManager:
        return self.view.undo_manager

    @property
    def animator(self) -> Animator:
        return self.view.animator