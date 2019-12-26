from typing import Optional, List

import pygame
from pygame.event import EventType
from pygame.time import Clock

from animator import Animator
from music_player import initialise_mixer, MusicPlayer
from navigator import Navigator
from resources import Resources
from undo import UndoManager
from views.map_view import MapView, MapViewParameters
from views.view import View

DEFAULT_WINDOW_SIZE = 640, 704


class App(Navigator):
    def __init__(self):
        self._keep_running = True
        self.resources: Optional[Resources] = None
        self.music_player: Optional[MusicPlayer] = None
        self.undo_manager = UndoManager()
        self.animator = Animator(self.undo_manager)
        self.current_view: Optional[View] = None
        self.clock = Clock()

    def on_init(self):
        initialise_mixer()
        pygame.init()
        pygame.mixer.music.load("resources/Puzzle-Dreams-3.mp3")
        pygame.mixer.music.play(-1)

        display = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        self._keep_running = True

        self.resources = Resources(display)
        self.music_player = MusicPlayer(self.resources, self.undo_manager)
        self.go_to_view(MapView, MapViewParameters(map_index=0))
        return True

    def go_to_view(self, view: type, parameters: any):
        if self.current_view:
            self.current_view.close()

        self.current_view: View = view(self.undo_manager, self.animator, self.music_player, self.resources, self)
        self.current_view.initialise(parameters)

    def on_events(self, events: List[EventType]):
        if not events:
            return

        for event in events:
            # Quit the game
            if event.type == pygame.QUIT:
                self._keep_running = False

            # Handle screen resizing
            if event.type == pygame.VIDEORESIZE:
                self.resources.display: pygame.SurfaceType = pygame.display.set_mode((event.w, event.h), self.resources.display.get_flags())

            if event.type == pygame.KEYDOWN:
                # Quit the game
                if event.key == pygame.K_ESCAPE:
                    self._keep_running = False

                # Full screen toggle
                if event.key == pygame.K_f:
                    flags = self.resources.display.get_flags()
                    new_flags = flags ^ pygame.FULLSCREEN
                    self.resources.display: pygame.SurfaceType = pygame.display.set_mode(self.resources.display.get_size(), new_flags)

        self.current_view.on_events(events)

    def pre_event_loop(self):
        self.animator.run_animations()
        self.current_view.pre_event_loop()

    def post_event_loop(self):
        self.current_view.post_event_loop()

    def draw(self):
        self.current_view.draw()
        pygame.display.update()

    @staticmethod
    def on_clean_up():
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._keep_running = False

        while self._keep_running:
            self.pre_event_loop()
            self.on_events(list(pygame.event.get()))
            self.post_event_loop()
            self.draw()
            self.clock.tick(60)

        App.on_clean_up()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
