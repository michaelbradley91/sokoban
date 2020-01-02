from typing import List, Optional

from constants.direction import Direction, direction_to_coordinate
from coordinate import Coordinate


class PresetGridAnimationPlayer:
    """
    A class for playing a preset animation. (An animation should not be empty)
    """
    def __init__(self, preset_grid_animation: "PresetGridAnimation"):
        self.__steps = preset_grid_animation.steps
        self.__next_position = 0
        self.reset()

    def reset(self):
        self.__next_position = 0

    @property
    def steps(self):
        return list(self.__steps)

    @property
    def is_finished(self) -> bool:
        return self.__next_position >= len(self.__steps)

    def play_next_step(self) -> Coordinate:
        """
        Get the next step in the animation. The position in the animation is updated.
        :return: the next coordination to move to.
        """
        if self.is_finished:
            return self.__steps[-1]

        coordinate = self.__steps[self.__next_position]
        self.__next_position += 1
        return coordinate

    @property
    def current_step(self) -> Coordinate:
        """
        Get the current step without incrementing the position
        :return: the current step
        """
        if self.__next_position == 0:
            return self.__steps[0]
        return self.__steps[self.__next_position - 1]

    def jump_to_step(self, position: int) -> Coordinate:
        """
        Jump to a specific step in the animation
        :param position: the step to jump to
        :return: the current step after the jump
        """
        self.__next_position = position + 1
        return self.current_step


class PresetGridAnimation:
    """
    A utility class to help coordinate a grid based animation
    """
    def __init__(self, start_position: Coordinate):
        self.__steps: List[Coordinate] = [start_position]

    @property
    def steps(self):
        return list(self.__steps)

    def insert_position(self, position: Coordinate, index: Optional[int] = None):
        """
        Insert a position into the animation.
        Note: does not update previously appended steps if inserted before them.
        :param position: the absolute position to add
        :param index: the index to insert into. Defaults to appending
        :return: nothing
        """
        if index is None:
            self.__steps.append(position)
        else:
            self.__steps.insert(index, position)

    def append_position(self, position: Coordinate):
        """ Alias for insert_position with no index """
        self.insert_position(position)

    def append_steps(self, *directions: Direction):
        """ Add several directional steps at once """
        for direction in directions:
            self.append_step(direction)

    def append_step(self, direction: Direction, *, amount: int = 1, repeat: int = 1):
        """
        Append a new step by moving the current position in the given direction by the amount specified.
        :param direction:
        :param amount: the amount to move by. Defaults to 1
        :param repeat: the number of times to repeat the step. Defaults to 1
        :return: nothing
        """
        coordinate_change = direction_to_coordinate(direction).scalar_multiply(amount)
        for r in range(repeat):
            self.__steps.append(self.__steps[-1] + coordinate_change)

    def create_player(self) -> PresetGridAnimationPlayer:
        """
        :return: a player to play the animation for you
        """
        return PresetGridAnimationPlayer(self)
