from time import time
from typing import NamedTuple, Tuple

from pygame.rect import Rect

from animations.animation import Animation
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
    def __init__(self, start: Coordinate, finish: Coordinate, number_of_images: int, travel_time: int,
                 image_time: int):
        """
        :param start: where the image should begin moving from
        :param finish: where the image should move to
        :param number_of_images: the number of images to cycle through
        :param travel_time: the time to take travelling from start to finish in milliseconds
        :param image_time: the time to spend showing each image in milliseconds

        Note: the images are played in the order they are passed in.
        The first image is assumed to be the final image.
        """
        super().__init__(lambda: self.update().finished, self.stop)
        self.__start = start
        self.__finish = finish
        self.__number_of_images = number_of_images
        self.__travel_time = travel_time
        self.__image_time = image_time
        self.__start_time = None
        self.__status: LinearAnimationState = LinearAnimationState(
            finished=False,
            image_index=0,
            position=(self.__start.x, self.__start.y)
        )
        self.__vector = finish - start

    def start(self):
        self.__start_time = time()

    def stop(self):
        self.__status = LinearAnimationState(
            position=(self.__finish.x, self.__finish.y),
            image_index=0,
            finished=True
        )

    def update(self) -> LinearAnimationState:
        """
        Update the animation status. Returns
        :return: the new linear animation status
        """
        if self.status.finished:
            return self.status

        if not self.__start_time:
            self.__start_time = time()

        now = time()
        percentage_travelled = ((now - self.__start_time) * 1000) / self.__travel_time

        if percentage_travelled >= 0.99999:
            # Done!
            self.__status = LinearAnimationState(
                position=(self.__finish.x, self.__finish.y),
                image_index=0,
                finished=True
            )
            return self.__status

        # Calculate the distance moved
        new_x = self.__start.x + (self.__vector.x * percentage_travelled)
        new_y = self.__start.y + (self.__vector.y * percentage_travelled)

        # Calculate the image to display
        image_to_show = int(((now - self.__start_time) * 1000) / self.__image_time) % self.__number_of_images

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
        if not self.__start_time:
            self.__start_time = time()

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
