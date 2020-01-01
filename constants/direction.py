from enum import Enum
from typing import Optional, Dict, Callable

import pygame

from coordinate import Coordinate


class Direction(Enum):
    left = 0,
    right = 1,
    up = 2,
    down = 3


def try_get_move_from_key(pressed_keys: Dict[int, bool]) -> Optional[Direction]:
    """
    Get a move from pressed keys. Returns None if no move key is pressed,
    and only returns the first move otherwise
    :param pressed_keys: the pressed keys
    :return: the direction of movement
    """
    if pressed_keys[pygame.K_UP]:
        return Direction.up
    elif pressed_keys[pygame.K_DOWN]:
        return Direction.down
    elif pressed_keys[pygame.K_RIGHT]:
        return Direction.right
    elif pressed_keys[pygame.K_LEFT]:
        return Direction.left
    return None


def coordinate_change_to_direction(coordinate_change: Coordinate) -> Direction:
    """
    Calculate the direction of a change. This assumes the change is only in one direction
    :param coordinate_change:  the coordinate change
    :return: the direction of the change
    """
    if coordinate_change.x > 0:
        return Direction.right
    if coordinate_change.x < 0:
        return Direction.left
    if coordinate_change.y > 0:
        return Direction.down
    if coordinate_change.y < 0:
        return Direction.up
    raise ValueError("No change so no direction!")


def direction_to_coordinate(direction: Direction) -> Coordinate:
    """
    Get a unit coordinate which, when added, moves another coordinate in the given direction.
    :param direction: the direction of the unit coordinate
    :return: the unit coordinate
    """
    if direction == Direction.up:
        return Coordinate(x=0, y=-1)
    elif direction == Direction.down:
        return Coordinate(x=0, y=1)
    elif direction == Direction.right:
        return Coordinate(x=1, y=0)
    elif direction == Direction.left:
        return Coordinate(x=-1, y=0)
    raise ValueError(f"Unknown direction: {direction.name}")


def direction_sorter(direction: Direction) -> Callable[[Coordinate], int]:
    """
    Get a sorting function that sorts by direction
    :param direction: the direction to sort in, so if the direction is right, the order is from left TO right
    :return: the sorting function that expects a coordinate
    """
    if direction == Direction.up:
        return lambda c: c.y
    elif direction == Direction.down:
        return lambda c: -c.y
    elif direction == Direction.right:
        return lambda c: -c.x
    elif direction == Direction.left:
        return lambda c: c.x
