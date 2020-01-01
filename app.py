import sys
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional, List, Tuple

import pygame
from OpenGL.raw.WGL.EXT import swap_control
from pygame.event import EventType
from pygame.time import Clock

from animator import Animator
from app_container import AppContainer
from layouts.layout import BasicLayout
from music_player import initialise_mixer, MusicPlayer
from navigator import Navigator
from opengl_support.helpers import init_opengl
from opengl_support.monkey_patching import monkey_patch
from resources import Resources, find_resource
from undo import UndoManager
from views.start_view import StartView, StartViewParameters
from views.view import View

DEFAULT_WINDOW_SIZE = 640, 704


monkey_patch()


class App(AppContainer, Navigator):
    """
    The starting app
    """
    def __init__(self):
        self._keep_running = True
        self.__resources: Optional[Resources] = None
        self.__music_player: Optional[MusicPlayer] = None
        self.__undo_manager = UndoManager()
        self.__animator = Animator(self.__undo_manager)
        self.__current_view: Optional[View] = None
        self.__last_window_size: Tuple[int, int] = DEFAULT_WINDOW_SIZE
        self.__layout: BasicLayout = BasicLayout(identifier="app_window")
        self.__container: AppContainer
        self.__clock = Clock()

    def on_init(self):
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

        # https://stackoverflow.com/questions/589064/how-to-enable-vertical-sync-in-opengl/589232#589232
        # Turn on vsync if possible
        if sys.platform == "win32":
            swap_control.wglSwapIntervalEXT(True)

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

    def draw_animated(self):
        self.__current_view.draw_animated()

    def quit(self):
        self._keep_running = False

    @staticmethod
    def on_clean_up():
        pygame.quit()

    def on_execute(self):
        # self.last_call = pygame.time.get_ticks
        previous_time = pygame.time.get_ticks()
        queue = Queue(maxsize=1)

        def just_tick(tick_queue, clock, display):

            def custom_ticks(last_call):
                start = pygame.time.get_ticks()
                start_duration = start - last_call
                # print(start_duration)
                # print("s:", start)
                target_delay = int(1000 / 60) - start_duration
                # print("Target:", target_delay)
                next_delay = target_delay - (pygame.time.get_ticks() - start)
                while next_delay > 0:
                    if next_delay > 3:
                        # print("Sleeping")
                        sleep((next_delay - 2) / 1000)
                    next_delay = target_delay - (pygame.time.get_ticks() - start)
                last_call = pygame.time.get_ticks()
                return (last_call - start) + start_duration

            last_call = pygame.time.get_ticks()
            while True:
                if display.get_flags() & pygame.FULLSCREEN:
                    # print("Full screen!")
                    tick_queue.put(0)
                else:

                    tick_queue.put(clock.tick(60))
                    last_call = pygame.time.get_ticks()

        if not self.on_init():
            self._keep_running = False

        tick_thread = Thread(target=just_tick, args=[queue, self.__clock, self.__resources.display])
        tick_thread.start()

        time_elapsed = 0
        total = 0

        while self._keep_running:
            events = list(pygame.event.get())
            self.pre_event_loop()
            self.on_events(events)
            self.post_event_loop()
            self.draw_static()
            if not self.resources.display.get_flags() & pygame.FULLSCREEN:
                queue.get()
            # time_elapsed = self.__clock.tick(60)
            # time_elapsed = self.__clock.tick_busy_loop(60)
            next_time = pygame.time.get_ticks()
            time_elapsed = next_time - previous_time
            previous_time = next_time
            if time_elapsed > 20:
                total += 1
                # print("t:", total, time_elapsed)
            self.__animator.run_animations(time_elapsed)
            self.draw_animated()
            pygame.display.flip()

        App.on_clean_up()


    def restart_opengl(self):
        init_opengl(self.__resources.display)
        self.__resources.reload()

    @property
    def undo_manager(self):
        return self.__undo_manager

    @property
    def animator(self):
        return self.__animator

    @property
    def music_player(self):
        return self.__music_player

    @property
    def resources(self):
        return self.__resources

    @property
    def navigator(self):
        return self


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
