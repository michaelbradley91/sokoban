from abc import ABC, abstractmethod

from app_container import UsesAppContainer, AppContainer
from layouts.layout import Layout, BasicLayout


class ComponentView(UsesAppContainer, ABC):
    """
    A component view, that can be reused in other views.
    """
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        """
        :param app_container: a container for useful app resources
        :param layout: the layout in which this container should be drawn
        """
        self.__app_container = app_container
        self.layout = layout

    def update_layout(self):
        """
        Utility for updating this component's layout by updating its containing layout.
        """
        self.layout.update_components()

    @property
    def app_container(self):
        return self.__app_container

    @abstractmethod
    def draw(self):
        pass
