from typing import List

from pygame.event import EventType

from app_container import AppContainer
from layouts.layout import BasicLayout
from views.view import View, ViewModel


class OptionsViewParameters:
    pass


class OptionsViewModel(ViewModel[OptionsViewParameters]):
    pass


class OptionsView(View[OptionsViewParameters, OptionsViewModel]):
    """
    The options screen that allows the modification of game settings
    """
    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

    def init(self):
        pass

    def close(self):
        pass

    def pre_event_loop(self):
        pass

    def on_events(self, events: List[EventType]):
        pass

    def post_event_loop(self):
        pass

    def draw_static(self):
        pass

    def post_animation_loop(self):
        pass

    def draw_animated(self):
        pass