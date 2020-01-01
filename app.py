import sys
from collections import defaultdict
from queue import Queue, Full
from threading import Thread
from typing import Optional, List, Tuple, Dict

import pygame
from OpenGL.WGL.EXT import swap_control
from pygame.event import EventType
from pygame.time import Clock

from animator import Animator
from app_container import AppContainer
from layouts.layout import BasicLayout
from music_player import initialise_mixer, MusicPlayer
from navigator import Navigator
from opengl_support.helpers import init_opengl, try_enable_vsync
import opengl_support.monkey_patching
from resources import Resources, find_resource
from undo import UndoManager
from views.start_view import StartView, StartViewParameters
from views.view import View

DEFAULT_WINDOW_SIZE = 640, 704
DEFAULT_TARGET_FRAME_RATE = 60
NUMBER_OF_ELAPSED_TIME_SAMPLES = 10
VSYNC_FAILING_TRIALS = 10000
VSYNC_FAILING_FACTOR = 1.5


opengl_support.monkey_patching.monkey_patch()


class AppClock:
    """
    An adaptive version of the pygame clock used to manage the frame rate
    in pygame
    """
    def __init__(self, target_frame_rate: int):
        self.__target_frame_rate = target_frame_rate
        self.__elapsed_time_samples: List[int] = []
        self.__vsync_enabled = False
        self.__vsync_working = False
        self.__vsync_not_working_count = 0
        self.__full_screen_enabled = False
        self.__last_ticks = pygame.time.get_ticks()
        self.__tick_thread_queue = Queue(maxsize=1)
        self.__tick_thread_kill_queue = Queue()
        self.__tick_thread: Thread = None
        self.__in_line_clock = Clock()

        self.reset_clock()

    @staticmethod
    def tick_thread(kill_queue: Queue, tick_queue: Queue, target_frame_rate: int):
        """
        A thread whose only job is to tick. This was found to be more accurate
        than running tick after CPU work, since it gives tick longer to sleep.
        :return: nothing
        """
        clock = Clock()
        while kill_queue.empty():
            clock.tick(target_frame_rate)
            try:
                tick_queue.put(None, timeout=2)
            except Full:
                # Needed to ensure that the thread does die
                pass

    def reset_clock(self):
        """
        Reset adaptive estimates made by the clock and other resources
        :return: nothing
        """
        self.__elapsed_time_samples.clear()
        self.__vsync_not_working_count = 0
        self.__vsync_working = self.__vsync_enabled
        self.__vsync_not_working_count = 0
        self.__last_ticks = pygame.time.get_ticks()
        self.__in_line_clock = Clock()
        self.restart_tick_thread()

    def set_target_frame_rate(self, target_frame_rate: int):
        """
        Set the target frame rate to run at
        :param target_frame_rate: the target frame rate
        :return: nothing
        """
        self.__target_frame_rate = target_frame_rate
        self.reset_clock()

    def set_vsync_enabled(self, enabled: bool):
        """
        Update the clock to state whether or not vsync is enabled.
        If enabled, the clock will try to allow pygame's own display flip
        to synchronise, but if it is detected this is not working,

        :param enabled: whether or not vsync is enabled
        :return: nothing
        """
        if self.__vsync_enabled != enabled:
            self.__vsync_enabled = enabled
            self.reset_clock()

    def set_full_screen(self, enabled: bool):
        """
        Update if full screen is enabled.
        It has been seen that with fullscreen turned on, thread synchronisation is actually worse.
        :param enabled: if full screen is enabled
        :return: nothing
        """
        if self.__full_screen_enabled != enabled:
            self.__full_screen_enabled = enabled
            self.reset_clock()

    def restart_tick_thread(self):
        """
        Restart the tick thread. Can be useful to heuristically try synchronising with the screen
        :return: nothing
        """
        if self.__tick_thread:
            self.__tick_thread_kill_queue.put(True)
            # The thread will now die after some time. (10 seconds)
            self.__tick_thread_queue = Queue(maxsize=1)
            self.__tick_thread_kill_queue = Queue()

        self.__tick_thread = Thread(target=AppClock.tick_thread, args=[
            self.__tick_thread_kill_queue, self.__tick_thread_queue, self.__target_frame_rate])
        self.__tick_thread.start()

    def stop(self):
        self.reset_clock()
        if self.__tick_thread:
            self.__tick_thread_kill_queue.put(True)
        self.__tick_thread.join()

    def add_elapsed_time_sample(self, elapsed_time: int):
        """
        Record the given elapsed time sample in seconds
        :param elapsed_time: the sample
        :return: nothing
        """
        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            self.__elapsed_time_samples.pop(0)

        self.__elapsed_time_samples.append(elapsed_time)

        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            average = sum(self.__elapsed_time_samples) / NUMBER_OF_ELAPSED_TIME_SAMPLES
            # Remove any significant outliers caused by video refreshes for example
            self.__elapsed_time_samples = [s for s in self.__elapsed_time_samples if (average / 5) < s < (5 * average)]

    def get_fps(self):
        """
        Get the FPS of None if it cannot be computed yet due to too few samples
        :return: the FPS
        """
        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            return int(10000 / sum(self.__elapsed_time_samples))
        else:
            return None

    def tick(self):
        if self.__vsync_enabled:
            if not self.__vsync_working:
                self.__vsync_not_working_count += 1
                if self.__vsync_not_working_count >= VSYNC_FAILING_TRIALS:
                    # Try again
                    self.__vsync_working = True
                    self.__vsync_not_working_count = 0

            # Check if the FPS target is working
            fps = self.get_fps()
            if self.__vsync_working and (not fps or fps < VSYNC_FAILING_FACTOR * self.__target_frame_rate):
                # "Working"
                new_ticks = pygame.time.get_ticks()
                elapsed_ticks = new_ticks - self.__last_ticks
                self.add_elapsed_time_sample(elapsed_ticks)
                self.__last_ticks = new_ticks
                return elapsed_ticks
            elif self.__vsync_working:
                # Failing so revert to throttling
                self.__vsync_working = False
                self.__vsync_not_working_count = 1

        # The above returned if vsync worked, so now we throttle
        if self.__full_screen_enabled:
            self.__in_line_clock.tick(self.__target_frame_rate)
        else:
            try:
                if self.__full_screen_enabled:
                    self.__tick_thread_queue.get(timeout=2)
            except Full:
                # Something went wrong?
                self.reset_clock()

        new_ticks = pygame.time.get_ticks()
        elapsed_ticks = new_ticks - self.__last_ticks
        self.add_elapsed_time_sample(elapsed_ticks)
        self.__last_ticks = new_ticks
        return elapsed_ticks


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
        print("Stopping")
        self.__app_clock.stop()
        print("Stopped")

    def tick(self) -> int:
        """
        Ticks the game clock and reports the time in milliseconds since the last
        tick occurred.
        :return:
        """

    def on_execute(self):
        total = 0
        last = pygame.time.get_ticks()
        if not self.on_init():
            self._keep_running = False
        while self._keep_running:
            self.__keys_pressed = pygame.key.get_pressed()
            events = list(pygame.event.get())
            self.pre_event_loop()
            self.on_events(events)
            self.post_event_loop()
            self.draw_static()
            next = pygame.time.get_ticks()
            print(next)
            elapsed_ticks = next - last
            last = next
            # elapsed_ticks = self.__app_clock.tick()
            if elapsed_ticks > 20:
                total += 1
            self.animator.run_animations(elapsed_ticks)
            self.post_animation_loop()
            self.draw_animated()
            pygame.display.flip()

        self.on_clean_up()

    def restart_opengl(self):
        vsync_enabled = try_enable_vsync()
        full_screen_enabled = bool(self.__resources.display.get_flags() & pygame.FULLSCREEN)
        self.__app_clock.set_vsync_enabled(vsync_enabled)
        self.__app_clock.set_full_screen(full_screen_enabled)
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
