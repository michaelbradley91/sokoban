from math import sqrt
from typing import Tuple


class Coordinate:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def normalise(self) -> Tuple[float, float]:
        """
        When considering this point like a vector, normalise x and y so the length
        is about 1. Returns (0, 0) if the coordinate is (0, 0)
        :return: the normalised vector as a tuple
        """
        if self.x == 0 and self.y == 0:
            return 0, 0

        factor = sqrt((self.__x * self.__x) + (self.__y * self.__y))
        return self.__x / factor, self.__y / factor

    def __iter__(self):
        return iter([self.x, self.y])

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, Coordinate):
            return other.x == self.x and other.y == self.y
        return False

    def __hash__(self):
        return self.x.__hash__() + self.y.__hash__()

    def __add__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(x=self.x + other.x, y=self.y + other.y)
        raise ValueError("Cannot add a non-coordinate")

    def __sub__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(x=self.x - other.x, y=self.y - other.y)
        raise ValueError("Cannot subtract a non-coordinate")

    def __str__(self):
        return f"({self.x}, {self.y})"
