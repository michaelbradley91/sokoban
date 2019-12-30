from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

import typing_inspect
from pygame.event import EventType

from app_container import AppContainer, UsesAppContainer
from layouts.layout import BasicLayout

T = TypeVar('T')
S = TypeVar('S')


class View(UsesAppContainer, ABC, Generic[T, S]):
    """
    An abstract representation of a view.
    Note: the constructor parameters are fixed. Other parameters should be provided by setting
    the correct parameter type.
    """

    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        self.parameters: Optional[T] = None
        self.model: Optional[S] = None
        self.__app_container = app_container
        self.__layout = layout

    def initialise(self, parameters: T):
        """ Initialise the view by saving the parameters and resetting various resources """
        self.parameters = parameters

        self.undo_manager.reset()
        self.animator.reset()
        self.music_player.reset()

        # Note: this only works if the view is an immediate subclass of View
        model_type = typing_inspect.get_args(typing_inspect.get_generic_bases(type(self))[0])[1]
        self.model: S = model_type(self)
        self.init()

    @property
    def layout(self):
        return self.__layout

    @property
    def app_container(self) -> AppContainer:
        return self.__app_container

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
    def close(self):
        """ Close any view specific resources """
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


class ViewModel(Generic[T], UsesAppContainer):
    def __init__(self, view: "View[T, ViewModel[T]]"):
        self.view = view

    @property
    def app_container(self) -> AppContainer:
        return self.view.app_container

    @property
    def parameters(self) -> T:
        return self.view.parameters
