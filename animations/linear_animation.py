from time import time
from typing import NamedTuple, Tuple, Callable

from pygame.rect import Rect

from animations.animation import Animation
from coordinate import Coordinate


class LinearAnimationStatus(NamedTuple):
    position: Tuple[float, float]
    image_index: int
    finished: bool


class LinearAnimation(Animation):
    """
    Represents a linear animation, meaning:
    - The animation moves from one rectangle to another in a straight line.
    - The images shown change at a fixed rate.

    Given the image list and start and finish locations, and the time between image
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
        self.__status: LinearAnimationStatus = LinearAnimationStatus(
            finished=False,
            image_index=0,
            position=(self.__start.x, self.__start.y)
        )
        self.__vector = finish - start

    def start(self):
        self.__start_time = time()

    def stop(self):
        self.__status = LinearAnimationStatus(
            position=(self.__finish.x, self.__finish.y),
            image_index=0,
            finished=True
        )

    def update(self) -> LinearAnimationStatus:
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
            self.__status = LinearAnimationStatus(
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

        self.__status = LinearAnimationStatus(
            position=(new_x, new_y),
            image_index=image_to_show,
            finished=False
        )
        return self.__status

    def draw(self, drawer: Callable[[Rect, int], None], grid_offset: Tuple[float, float], square_size: int):
        """
        Draw the sprite at the correct position
        :param drawer: the function to use to draw at the correct location, which will be given the rect
                       and image index in the animation
        :param grid_offset: the offset to the grid
        :param square_size: the size of each square
        :return: nothing
        """
        if not self.__start_time:
            self.__start_time = time()

        position = self.status.position
        new_x = grid_offset[0] + int(position[0] * square_size)
        new_y = grid_offset[1] + int(position[1] * square_size)
        new_rect = Rect((new_x, new_y), (square_size, square_size))
        image_index = self.status.image_index
        drawer(new_rect, image_index)

    @property
    def status(self) -> LinearAnimationStatus:
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