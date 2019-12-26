from typing import TYPE_CHECKING

import pygame
from undo import UndoManager

if TYPE_CHECKING:
    from resources import Resources


def initialise_mixer():
    pygame.mixer.init(channels=2, buffer=128)


class MusicPlayer:
    """
    A music player responsible for playing sounds.
    Uses the undo manager to cancel sounds if a move fails.
    """
    def __init__(self, resources: "Resources", undo_manager: UndoManager):
        self.resources = resources
        self.undo_manager = undo_manager

    def play_crate_slide(self):
        self.resources.crate_sound.play()
        self.undo_manager.register_cancel(self.resources.crate_sound.stop)

    def play_crate_moved_onto_goal(self):
        self.resources.crate_success_sound.play()
        self.undo_manager.register_cancel(self.resources.crate_success_sound.stop)

    def play_you_win(self):
        # We use the second channel to allow playing the win music on top of a crate noise
        pygame.mixer.Channel(1).play(self.resources.win_sound)
        self.undo_manager.register_cancel(self.resources.win_sound.stop)

    def reset(self):
        """
        Stop all sounds
        :return: nothing
        """
        self.resources.crate_sound.stop()
        self.resources.crate_success_sound.stop()
        self.resources.win_sound.stop()
