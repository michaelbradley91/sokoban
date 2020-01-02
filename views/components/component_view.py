from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app_container import UsesAppContainer, AppContainer
from layouts.layout import Layout, BasicLayout


class ComponentViewModel(UsesAppContainer):
    """ The view model for a component """
    def __init__(self, app_container: AppContainer):
        self.__app_container = app_container

    @property
    def app_container(self):
        return self.__app_container


T = TypeVar('T', bound=Layout)
S = TypeVar('S', bound=ComponentViewModel)


class ComponentView(UsesAppContainer, ABC, Generic[S, T]):
    """
    A component view, that can be reused in other views.
    """
    def __init__(self, app_container: AppContainer, model: S, layout: T):
        """
        :param app_container: a container for useful app resource
        :param model: the view model for this component view
        :param layout: the layout in which this container should be drawn
        """
        self.__app_container = app_container
        self.__model = model
        self.layout: T = layout

    def update_layout(self):
        """
        Utility for updating this component's layout by updating its containing layout.
        """
        self.layout.update_components()

    @property
    def app_container(self):
        return self.__app_container

    @property
    def model(self) -> S:
        return self.__model

    @abstractmethod
    def draw_static(self):
        pass

    @abstractmethod
    def draw_animated(self):
        pass
