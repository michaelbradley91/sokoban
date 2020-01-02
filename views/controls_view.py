from typing import List

from pygame.event import EventType

from app_container import AppContainer
from layouts.layout import BasicLayout
from views.view import ViewModel, View


class ControlsViewParameters:
    pass


class ControlsViewModel(ViewModel[ControlsViewParameters]):
    def __init__(self, view: "ControlsView"):
        super().__init__(view)


class ControlsView(View[ControlsViewParameters, ControlsViewModel]):
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