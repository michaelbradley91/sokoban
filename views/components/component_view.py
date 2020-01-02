from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app_container import UsesAppContainer, AppContainer
from layouts.layout import Layout, BasicLayout

T = TypeVar('T', bound=Layout)


class ComponentView(UsesAppContainer, ABC, Generic[T]):
    """
    A component view, that can be reused in other views.
    """
    def __init__(self, app_container: AppContainer, layout: T):
        """
        :param app_container: a container for useful app resources
        :param layout: the layout in which this container should be drawn
        """
        self.__app_container = app_container
        self.layout: T = layout

    def update_layout(self):
        """
        Utility for updating this component's layout by updating its containing layout.
        """
        self.layout.update_components()

    @property
    def app_container(self):
        return self.__app_container

    @abstractmethod
    def draw_static(self):
        pass

    @abstractmethod
    def draw_animated(self):
        pass
