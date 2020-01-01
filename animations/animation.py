from abc import abstractmethod, ABC
from typing import Callable


class Animation(ABC):
    """
    Represents an abstract animation object
    """
    def __init__(self, animate: Callable[[int], bool], cancel: Callable):
        self.__animate = animate
        self.__cancel = cancel

    @abstractmethod
    def start(self):
        pass

    def animate(self, time_elapsed: int) -> bool:
        """
        Update this animation object
        :param time_elapsed: the time elapsed in milliseconds
        :return:
        """
        return self.__animate(time_elapsed)

    def cancel(self):
        self.__cancel()
