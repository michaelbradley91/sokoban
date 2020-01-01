from typing import List

from animations.animation import Animation
from undo import UndoManager


class Animator:
    """
    Manages any animations on the grid to ensure they get executed
    """
    def __init__(self, undo_manager: UndoManager):
        self.__current_animations: List[Animation] = []
        self.undo_manager = undo_manager

    def reset(self):
        """
        Stop all running animations and clear out animations
        :return: nothing
        """
        for animation in self.__current_animations:
            animation.cancel()

        self.__current_animations = []

    def animating(self) -> bool:
        """
        :return: True if there are any animations running. False otherwise.
        """
        return len(self.__current_animations) > 0

    def add_animation(self, animation: Animation):
        """
        Add an animation to be run.
        :param animation: a callable function that returns true when the animation is complete.
        :return: nothing
        """
        self.__current_animations.append(animation)
        animation.start()

        self.undo_manager.register_cancel(animation.cancel)

    def cancel_animation(self, animation: Animation):
        """
        Remove an animation and cancel it
        :param animation: the animation to cancel
        :return: nothing
        """
        self.__current_animations.remove(animation)
        animation.cancel()

    def run_animations(self, time_elapsed: int):
        """
        Run all of the animations. Animations can finish after being run.
        :param time_elapsed: the amount of time elapsed since the last animation run
                             in milliseconds.
        :return: nothing
        """
        remaining_animations = []
        for index, animation in enumerate(self.__current_animations):
            finished = animation.animate(time_elapsed)
            if not finished:
                remaining_animations.append(animation)
        self.__current_animations = remaining_animations
