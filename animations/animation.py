from abc import abstractmethod, ABC
from typing import Callable


class Animation(ABC):
    """
    Represents an abstract animation object
    """
    def __init__(self, animate: Callable[[], bool], cancel: Callable):
        self.__animate = animate
        self.__cancel = cancel

    @abstractmethod
    def start(self):
        pass

    def animate(self) -> bool:
        return self.__animate()

    def cancel(self):
        self.__cancel()
