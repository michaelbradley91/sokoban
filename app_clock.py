from typing import List

import pygame
from pygame.time import Clock

NUMBER_OF_ELAPSED_TIME_SAMPLES = 10
VSYNC_FAILING_TRIALS = 10000
VSYNC_FAILING_FACTOR = 1.5


class AppClock:
    """
    An adaptive version of the pygame clock used to manage the frame rate
    in pygame
    """
    def __init__(self, target_frame_rate: int):
        self.__target_frame_rate = target_frame_rate
        self.__elapsed_time_samples: List[int] = []
        self.__vsync_enabled = False
        self.__vsync_working = False
        self.__vsync_not_working_count = 0
        self.__last_ticks = pygame.time.get_ticks()
        self.__clock = Clock()

        self.reset_clock()

    def reset_clock(self):
        """
        Reset adaptive estimates made by the clock and other resources
        :return: nothing
        """
        self.__elapsed_time_samples.clear()
        self.__vsync_not_working_count = 0
        self.__vsync_working = self.__vsync_enabled
        self.__vsync_not_working_count = 0
        self.__last_ticks = pygame.time.get_ticks()
        self.__clock = Clock()

    def set_target_frame_rate(self, target_frame_rate: int):
        """
        Set the target frame rate to run at
        :param target_frame_rate: the target frame rate
        :return: nothing
        """
        self.__target_frame_rate = target_frame_rate
        self.reset_clock()

    def set_vsync_enabled(self, enabled: bool):
        """
        Update the clock to state whether or not vsync is enabled.
        If enabled, the clock will try to allow pygame's own display flip
        to synchronise, but if it is detected this is not working,

        :param enabled: whether or not vsync is enabled
        :return: nothing
        """
        if self.__vsync_enabled != enabled:
            self.__vsync_enabled = enabled
            self.reset_clock()

    def add_elapsed_time_sample(self, elapsed_time: int):
        """
        Record the given elapsed time sample in seconds
        :param elapsed_time: the sample
        :return: nothing
        """
        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            self.__elapsed_time_samples.pop(0)

        self.__elapsed_time_samples.append(elapsed_time)

        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            average = sum(self.__elapsed_time_samples) / NUMBER_OF_ELAPSED_TIME_SAMPLES
            # Remove any significant outliers caused by video refreshes for example
            self.__elapsed_time_samples = [s for s in self.__elapsed_time_samples if (average / 5) < s < (5 * average)]

    def get_fps(self):
        """
        Get the FPS of None if it cannot be computed yet due to too few samples
        :return: the FPS
        """
        if len(self.__elapsed_time_samples) == NUMBER_OF_ELAPSED_TIME_SAMPLES:
            return int(10000 / sum(self.__elapsed_time_samples))
        else:
            return None

    def tick(self):
        if self.__vsync_enabled:
            if not self.__vsync_working:
                self.__vsync_not_working_count += 1
                if self.__vsync_not_working_count >= VSYNC_FAILING_TRIALS:
                    # Try again
                    self.__vsync_working = True
                    self.__vsync_not_working_count = 0

            # Check if the FPS target is working
            fps = self.get_fps()
            if self.__vsync_working and (not fps or fps < VSYNC_FAILING_FACTOR * self.__target_frame_rate):
                # "Working"
                new_ticks = pygame.time.get_ticks()
                elapsed_ticks = new_ticks - self.__last_ticks
                self.add_elapsed_time_sample(elapsed_ticks)
                self.__last_ticks = new_ticks
                return elapsed_ticks
            elif self.__vsync_working:
                # Failing so revert to throttling
                self.__vsync_working = False
                self.__vsync_not_working_count = 1

        # The above returned if vsync worked, so now we throttle
        self.__clock.tick(self.__target_frame_rate)
        new_ticks = pygame.time.get_ticks()
        elapsed_ticks = new_ticks - self.__last_ticks
        self.add_elapsed_time_sample(elapsed_ticks)
        self.__last_ticks = new_ticks
        return elapsed_ticks