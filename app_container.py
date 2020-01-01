from abc import ABC, abstractmethod
from typing import Dict

from animator import Animator
from music_player import MusicPlayer
from navigator import Navigator
from resources import Resources
from undo import UndoManager


class AppContainer(ABC):
    """
    A wrapper for the app which contains lots of objects needed globally
    """
    @property
    @abstractmethod
    def undo_manager(self) -> UndoManager:
        pass

    @property
    @abstractmethod
    def animator(self) -> Animator:
        pass

    @property
    @abstractmethod
    def music_player(self) -> MusicPlayer:
        pass

    @property
    @abstractmethod
    def resources(self) -> Resources:
        pass

    @property
    @abstractmethod
    def navigator(self) -> Navigator:
        pass

    @property
    @abstractmethod
    def keys_pressed(self) -> Dict[int, bool]:
        pass


class UsesAppContainer(ABC):
    """
    A utility to class to simplify access to objects in the app container
    """
    @property
    @abstractmethod
    def app_container(self) -> AppContainer:
        pass

    @property
    def undo_manager(self) -> UndoManager:
        return self.app_container.undo_manager

    @property
    def animator(self) -> Animator:
        return self.app_container.animator

    @property
    def music_player(self) -> MusicPlayer:
        return self.app_container.music_player

    @property
    def resources(self) -> Resources:
        return self.app_container.resources

    @property
    def navigator(self) -> Navigator:
        return self.app_container.navigator

    @property
    def keys_pressed(self) -> Dict[int, bool]:
        return self.app_container.keys_pressed
