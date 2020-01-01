from collections import defaultdict
from typing import Optional, List, Tuple, Dict

import pygame
from pygame.event import EventType

import opengl_support.monkey_patching
from animator import Animator
from app_clock import AppClock
from app_container import AppContainer
from layouts.layout import BasicLayout
from music_player import initialise_mixer, MusicPlayer
from navigator import Navigator
from opengl_support.helpers import init_opengl, try_enable_vsync, try_to_be_dpi_aware
from resources import Resources, find_resource
from undo import UndoManager
from views.start_view import StartView, StartViewParameters
from views.view import View

DEFAULT_WINDOW_SIZE = 640, 704
DEFAULT_TARGET_FRAME_RATE = 60


class App(AppContainer, Navigator):
    """
    The starting app
    """
    def __init__(self):
        self._keep_running = True
        self.__target_frame_Rate = DEFAULT_TARGET_FRAME_RATE
        self.__resources: Optional[Resources] = None
        self.__music_player: Optional[MusicPlayer] = None
        self.__undo_manager = UndoManager()
        self.__animator = Animator(self.__undo_manager)
        self.__current_view: Optional[View] = None
        self.__last_window_size: Tuple[int, int] = DEFAULT_WINDOW_SIZE
        self.__layout: BasicLayout = BasicLayout(identifier="app_window")
        self.__container: AppContainer
        self.__app_clock = AppClock(self.__target_frame_Rate)
        self.__keys_pressed: Dict[int, bool] = defaultdict(lambda: False)

    def on_init(self):
        opengl_support.monkey_patching.monkey_patch()
        try_to_be_dpi_aware()
        initialise_mixer()
        pygame.init()
        pygame.mixer.music.load(find_resource("resources/Puzzle-Dreams-3.mp3"))
        pygame.mixer.music.play(-1)

        display = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE |
                                          pygame.OPENGL)
        self._keep_running = True
        self.__resources = Resources(display)
        self.__music_player = MusicPlayer(self.__resources, self.__undo_manager)
        self.go_to_view(StartView, StartViewParameters())
        self.restart_opengl()

        return True

    def go_to_view(self, view: type, parameters: any):
        if self.__current_view:
            self.__current_view.close()
        self.__layout.remove_layout()
        self.__current_view: View = view(self, self.__layout)
        self.__current_view.initialise(parameters)
        self.__layout.update_rect(self.__resources.display.get_rect())

    def on_events(self, events: List[EventType]):
        if not events:
            return

        for event in events:
            # Quit the game
            if event.type == pygame.QUIT:
                self._keep_running = False

            # Handle screen resizing
            if event.type == pygame.VIDEORESIZE:
                self.__resources.display: pygame.SurfaceType = pygame.display.set_mode(
                    (event.w, event.h), self.__resources.display.get_flags())
                if not self.__resources.display.get_flags() & pygame.FULLSCREEN:
                    self.__last_window_size = event.w, event.h
                self.__layout.update_rect(self.__resources.display.get_rect())
                self.restart_opengl()

            if event.type == pygame.KEYDOWN:
                # Quit the game
                if event.key == pygame.K_ESCAPE:
                    self._keep_running = False

                # Full screen toggle
                if event.key == pygame.K_f:
                    flags = self.__resources.display.get_flags()
                    if flags & pygame.FULLSCREEN:
                        size = self.__last_window_size
                    else:
                        size = pygame.display.list_modes()[0]
                    new_flags = (flags ^ pygame.FULLSCREEN) | pygame.RESIZABLE
                    self.__resources.display: pygame.SurfaceType = pygame.display.set_mode(size, new_flags)
                    self.__layout.update_rect(self.__resources.display.get_rect())
                    self.restart_opengl()

        self.__current_view.on_events(events)

    def pre_event_loop(self):
        self.__current_view.pre_event_loop()

    def post_event_loop(self):
        self.__current_view.post_event_loop()

    def draw_static(self):
        self.__current_view.draw_static()

    def post_animation_loop(self):
        self.__current_view.post_animation_loop()

    def draw_animated(self):
        self.__current_view.draw_animated()

    def quit(self):
        self._keep_running = False

    def on_clean_up(self):
        pygame.quit()

    def tick(self) -> int:
        """
        Ticks the game clock and reports the time in milliseconds since the last
        tick occurred.
        :return:
        """

    def on_execute(self):
        if not self.on_init():
            self._keep_running = False
        while self._keep_running:
            self.__keys_pressed = pygame.key.get_pressed()
            events = list(pygame.event.get())
            self.pre_event_loop()
            self.on_events(events)
            self.post_event_loop()
            self.draw_static()
            elapsed_ticks = self.__app_clock.tick()
            self.animator.run_animations(elapsed_ticks)
            self.post_animation_loop()
            self.draw_animated()
            pygame.display.flip()

        self.on_clean_up()

    def restart_opengl(self):
        vsync_enabled = try_enable_vsync()
        self.__app_clock.set_vsync_enabled(vsync_enabled)
        self.__app_clock.reset_clock()
        init_opengl(self.__resources.display)
        self.__resources.reload()

    @property
    def undo_manager(self) -> UndoManager:
        return self.__undo_manager

    @property
    def animator(self) -> Animator:
        return self.__animator

    @property
    def music_player(self) -> MusicPlayer:
        return self.__music_player

    @property
    def resources(self) -> Resources:
        return self.__resources

    @property
    def navigator(self) -> Navigator:
        return self

    @property
    def keys_pressed(self) -> Dict[int, bool]:
        return self.__keys_pressed


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
