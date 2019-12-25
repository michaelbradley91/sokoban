from typing import List

from animator import Animator
from coordinate import Coordinate
from grid import Grid
from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.player import PlayerPiece
from pieces.wall import WallPiece
from resources import Resources
from undo import UndoManager


def read_map(undo_manager: UndoManager, resources: Resources, animator: Animator, custom_map: List[List[str]]) -> Grid:
    height = len(custom_map)
    if height <= 0:
        raise ValueError("No empty maps allowed! (height)")

    width = len(custom_map[0])
    if width <= 0:
        raise ValueError("No empty maps allowed! (width)")

    for row in custom_map:
        if len(row) != width:
            raise ValueError("Maps must be rectangles")

    grid = Grid(undo_manager, animator, resources, width, height)
    for y, row in enumerate(custom_map):
        for x, string in enumerate(row):
            if string == 'W':
                grid.add_piece(WallPiece(grid, undo_manager, animator, resources), Coordinate(x, y))
            if string == 'P':
                grid.add_piece(PlayerPiece(grid, undo_manager, animator, resources), Coordinate(x, y))
            if string == 'B':
                grid.add_piece(CratePiece(grid, undo_manager, animator, resources), Coordinate(x, y))
            if string == 'G':
                grid.add_piece(GoalPiece(grid, undo_manager, animator, resources), Coordinate(x, y))

    return grid
