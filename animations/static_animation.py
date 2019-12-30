from time import time

from animations.animation import Animation


class StaticAnimation(Animation):
    """
    Represents a static animation that just cycles through images over time
    """

    def __init__(self, number_of_images: int, image_time: int):
        super().__init__(lambda: self.update(), self.stop)
        self.__number_of_images = number_of_images
        self.__image_time = image_time
        self.__start_time = None
        self.__image_index = 0
        self.__finished = False

    def start(self):
        self.__start_time = time()

    def stop(self):
        self.__image_index = 0
        self.__start_time = None
        self.__finished = True

    def update(self) -> bool:
        """
        Update the animation status.
        :return: False to indicate the animation is not yet finished, or True if it has been stopped.
        """
        if self.is_finished:
            return True

        if not self.__start_time:
            self.__start_time = time()

        now = time()
        # Calculate the image to display
        self.__image_index = int(((now - self.__start_time) * 1000) / self.__image_time) % self.__number_of_images
        return False

    @property
    def image_index(self) -> int:
        """
        Return the linear animation status from the last update.
        :return: the current linear animation status
        """
        return self.__image_index

    @property
    def is_finished(self) -> bool:
        """
        :return: whether or not this animation is finished based on the last update
        """
        return self.__finished
