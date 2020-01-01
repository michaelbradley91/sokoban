from cmath import sqrt
from time import time
from typing import NamedTuple, Tuple, Callable, Optional

from pygame.rect import Rect

from animations.animation import Animation
from constants.direction import coordinate_change_to_direction, direction_to_coordinate
from coordinate import Coordinate


class LinearAnimationState(NamedTuple):
    position: Tuple[float, float]
    image_index: int
    finished: bool


class LinearAnimationResult(NamedTuple):
    rect: Rect
    image_index: int
    finished: bool


class LinearAnimation(Animation):
    """
    Represents a linear animation, meaning:
    - The animation moves from one rectangle to another in a straight line.
    - The images shown change at a fixed rate.

    Given the number of images and start and finish locations, and the time between image
    changes and the time to spend getting from start to finish,
    this object can report on what to show at each instance, and when it is finished.
    """
    def __init__(self, start: Tuple[float, float], finish: Tuple[float, float], number_of_images: int, travel_time: int,
                 image_time: int, finished: Optional[Callable[["LinearAnimation"], None]]):
        """
        :param start: where the image should begin moving from
        :param finish: where the image should move to
        :param number_of_images: the number of images to cycle through
        :param travel_time: the time to take travelling from start to finish in milliseconds
        :param image_time: the time to spend showing each image in milliseconds
        :param finished: an optional callback for when this animation has just finished.

        Note: the images are played in the order they are passed in.
        The first image is assumed to be the final image.
        """
        super().__init__(lambda time_elapsed: self.update(time_elapsed).finished, self.stop)
        self.__start = start
        self.__finish = finish
        self.__number_of_images = number_of_images
        self.__travel_time = travel_time
        self.__image_time = image_time
        self.__total_time_elapsed = 0
        self.__status: LinearAnimationState = LinearAnimationState(
            finished=False,
            image_index=0,
            position=(self.__start[0], self.__start[1])
        )
        if not finished:
            self.__finished: Callable[["LinearAnimation"], None] = lambda l: None
        else:
            self.__finished: Callable[["LinearAnimation"], None] = finished

    def start(self):
        pass

    def stop(self):
        self.__status = LinearAnimationState(
            position=(self.__finish[0], self.__finish[1]),
            image_index=0,
            finished=True
        )

    def extend(self, amount: float) -> LinearAnimationState:
        """
        Extend this animation by the given amount in its current direction and at the same speed.
        :param amount: the amount to extend by
        :return: the new animation state. Note that it is updated automatically with the previous elapsed time
        since the last update. (This time is not truncated if the animation just finished)
        """
        if amount <= 0:
            return self.update(0)
        normalised = self.vector_normalised
        distance = self.vector[0] + (normalised[0] * amount), self.vector[1] + (normalised[1] * amount)
        self.__finish = self.__start[0] + distance[0], self.__start[1] + distance[1]
        self.__finished = False
        return self.update(0)

    def update(self, time_elapsed: int) -> LinearAnimationState:
        """
        Update the animation status.
        :param time_elapsed: the amount of time that has elapsed since the last update
        :return: the new linear animation status
        """
        if self.status.finished:
            return self.status

        self.__total_time_elapsed += time_elapsed

        vector = self.__finish[0] - self.__start[0], self.__finish[1] - self.__start[1]
        percentage_travelled = self.__total_time_elapsed / self.__travel_time

        if percentage_travelled >= 0.99999:
            self.__status = LinearAnimationState(
                position=(self.__finish[0], self.__finish[1]),
                image_index=0,
                finished=True
            )
            self.__finished(self)
            return self.__status

        # Calculate the distance moved
        new_x = self.__start[0] + (vector[0] * percentage_travelled)
        new_y = self.__start[1] + (vector[1] * percentage_travelled)

        # Calculate the image to display
        image_to_show = int(self.__total_time_elapsed / self.__image_time) % self.__number_of_images

        self.__status = LinearAnimationState(
            position=(new_x, new_y),
            image_index=image_to_show,
            finished=False
        )
        return self.__status

    def calculate(self, grid_offset: Tuple[float, float], square_size: int) -> LinearAnimationResult:
        """
        Calculate the status of the animation, which means to get its current position on screen
        and the image index that should be shown, as well as whether or not the animation has finished.
        :param grid_offset: the offset to the grid
        :param square_size: the size of each square (i.e.: a single coordinate)
        :return: the linear animation status
        """
        position = self.status.position
        new_x = grid_offset[0] + int(position[0] * square_size)
        new_y = grid_offset[1] + int(position[1] * square_size)
        rect = Rect((new_x, new_y), (square_size, square_size))
        image_index = self.status.image_index
        return LinearAnimationResult(
            image_index=image_index,
            rect=rect,
            finished=self.status.finished
        )

    @property
    def vector(self) -> Tuple[float, float]:
        return self.__finish[0] - self.__start[0], self.__finish[1] - self.__finish[0]

    @property
    def vector_normalised(self) -> Tuple[float, float]:
        v = self.vector
        if v[0] == 0 and v[1] == 0:
            return 0, 0

        length = sqrt((v[0] * v[0]) + (v[1] * v[1]))
        return v[0] / length, v[1] / length

    @property
    def status(self) -> LinearAnimationState:
        """
        Return the linear animation status from the last update.
        :return: the current linear animation status
        """
        return self.__status

    @property
    def is_finished(self) -> bool:
        """
        :return: whether or not this animation is finished based on the last update
        """
        return self.status.finished
