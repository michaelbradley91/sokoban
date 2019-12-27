from typing import Optional, List, Tuple

import pygame
from pygame.event import EventType
from pygame.rect import Rect
from pygame.time import Clock

from animator import Animator
from layouts.layout import BasicLayout
from music_player import initialise_mixer, MusicPlayer
from navigator import Navigator
from opengl_helpers import opengl_enable_settings, opengl_load_texture
from resources import Resources, find_resource
from undo import UndoManager
from views.map_view import MapView, MapViewParameters
from views.view import View
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def reset_open_gl(display: pygame.SurfaceType):
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Orthogonal projection for 2d coordinates
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, display.get_width(), display.get_height(), 0, 0, 1)
    glMatrixMode(GL_MODELVIEW)

# Look here: https://stackoverflow.com/questions/27513270/retained-mode-to-draw-2d-texture-image/27522069

def texture_to_opengl_texture(texture: pygame.SurfaceType):
    image = pygame.image.tostring(texture, "RGBA", False)

    i = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, i)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture.get_width(), texture.get_height(),
                 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    #
    # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    return i


def load_texture(texture_name):
    texture_surface = pygame.image.load(texture_name)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", False)

    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    return texture_id


DEFAULT_WINDOW_SIZE = 640, 704


class App(Navigator):
    def __init__(self):
        self._keep_running = True
        self.resources: Optional[Resources] = None
        self.music_player: Optional[MusicPlayer] = None
        self.undo_manager = UndoManager()
        self.animator = Animator(self.undo_manager)
        self.current_view: Optional[View] = None
        self.last_window_size: Tuple[int, int] = DEFAULT_WINDOW_SIZE
        self.layout: BasicLayout = BasicLayout(identifier="app_window")
        self.clock = Clock()

    def on_init(self):
        # initialise_mixer()
        pygame.init()
        # pygame.mixer.music.load(find_resource("resources/Puzzle-Dreams-3.mp3"))
        # pygame.mixer.music.play(-1)
        display = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        reset_open_gl(display)
        self.resources = Resources(display)
        self.texture = load_texture("resources/sokoban_tilesheet.png")
        self.text = texture_to_opengl_texture(pygame.font.Font("resources/heygorgeous.ttf", 128).render("You win!", True, pygame.Color("red")))
        self._keep_running = True

        # self.music_player = MusicPlayer(self.resources, self.undo_manager)
        # self.go_to_view(MapView, MapViewParameters(map_index=0))
        return True

    def go_to_view(self, view: type, parameters: any):
        if self.current_view:
            self.current_view.close()
        self.layout.remove_layout()
        self.current_view: View = view(self.undo_manager, self.animator, self.music_player, self.resources,
                                       self, self.layout)
        self.current_view.initialise(parameters)
        self.layout.update_rect(self.resources.display.get_rect())

    def on_events(self, events: List[EventType]):
        if not events:
            return

        for event in events:
            # Quit the game
            if event.type == pygame.QUIT:
                self._keep_running = False

            # Handle screen resizing
            if event.type == pygame.VIDEORESIZE:
                self.resources.display: pygame.SurfaceType = pygame.display.set_mode(
                    (event.w, event.h), self.resources.display.get_flags())
                if not self.resources.display.get_flags() & pygame.FULLSCREEN:
                    self.last_window_size = event.w, event.h
                self.layout.update_rect(self.resources.display.get_rect())
                reset_open_gl(self.resources.display)
                self.texture = load_texture("resources/sokoban_tilesheet.png")
                self.text = texture_to_opengl_texture(
                    pygame.font.Font("resources/heygorgeous.ttf", 128).render("You win!", True, pygame.Color("red")))

            if event.type == pygame.KEYDOWN:
                # Quit the game
                if event.key == pygame.K_ESCAPE:
                    self._keep_running = False

                # Full screen toggle
                if event.key == pygame.K_f:
                    flags = self.resources.display.get_flags()
                    if flags & pygame.FULLSCREEN:
                        size = self.last_window_size
                    else:
                        size = pygame.display.list_modes()[0]
                    new_flags = (flags ^ pygame.FULLSCREEN) | pygame.RESIZABLE
                    self.resources.display: pygame.SurfaceType = pygame.display.set_mode(size, new_flags)
                    self.layout.update_rect(self.resources.display.get_rect())
                    reset_open_gl(self.resources.display)
                    self.texture = load_texture("resources/sokoban_tilesheet.png")
                    self.text = texture_to_opengl_texture(
                       pygame.font.Font("resources/heygorgeous.ttf", 128).render("You win!", True, pygame.Color("red")))

        # self.current_view.on_events(events)

    def pre_event_loop(self):
        # self.animator.run_animations()
        # self.current_view.pre_event_loop()
        pass

    def post_event_loop(self):
        # self.current_view.post_event_loop()
        pass

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        width = self.resources.display.get_width()
        height = self.resources.display.get_height()
        glTexCoord2f(0.0, 0.0)
        glVertex3i(0, 0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3i(width, 0, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3i(width, height, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3i(0, height, 0)
        glEnd()

        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        width = self.resources.display.get_width()
        height = self.resources.display.get_height()
        glTexCoord2f(0.0, 0.0)
        glVertex3i(0, 0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3i(width // 2, 0, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3i(width // 2, height // 2, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3i(0, height // 2, 0)
        glEnd()

        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.text)
        glBegin(GL_QUADS)
        width = self.resources.display.get_width()
        height = self.resources.display.get_height()
        glTexCoord2f(0.0, 0.0)
        glVertex3i(width // 2, height // 2, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3i(width, height // 2, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3i(width, height, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3i(width // 2, height, 0)
        glEnd()
        #
        # glBegin(GL_QUADS)
        # glTexCoord2f(0.0, 0.0)
        # glVertex3f(-0.5, -0.5, 0.0)
        # glTexCoord2f(1.0, 0.0)
        # glVertex3f(0.5, -0.5, 0.0)
        # glTexCoord2f(1.0, 1.0)
        # glVertex3f(0.5, 0.5, 0.0)
        # glTexCoord2f(0.0, 1.0)
        # glVertex3f(-0.5, 0.5, 0.0)
        # glEnd()

        # glBegin(GL_QUADS)
        # glColor3f(1, 0, 0)
        # glVertex2f(-0.2, -0.2)
        # glVertex2f(0.2, -0.2)
        # glVertex2f(0.2, 0.2)
        # glVertex2f(-0.2, 0.2)
        # glEnd()

        pygame.display.flip()

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
