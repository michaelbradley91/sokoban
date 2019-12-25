from typing import Callable, List

from undo import UndoManager


class Animation:
    """
    Represents an abstract animation object
    """
    def __init__(self, animate: Callable[[], bool], cancel: Callable):
        self.__animate = animate
        self.__cancel = cancel

    def animate(self) -> bool:
        return self.__animate()

    def cancel(self):
        self.__cancel()


class Animator:
    """
    Manages any animations on the grid to ensure they get executed
    """
    def __init__(self, undo_manager: UndoManager):
        self.__current_animations: List[Animation] = []
        self.undo_manager = undo_manager

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
        self.undo_manager.register_cancel(animation.cancel)

    def cancel_animation(self, animation: Animation):
        """
        Remove an animation and cancel it
        :param animation: the animation to cancel
        :return: nothing
        """
        self.__current_animations.remove(animation)
        animation.cancel()

    def run_animations(self):
        """
        Run all of the animations. Animations can finish after being run.
        :return: nothing
        """
        remaining_animations = []
        for index, animation in enumerate(self.__current_animations):
            finished = animation.animate()
            if not finished:
                remaining_animations.append(animation)
        self.__current_animations = remaining_animations
