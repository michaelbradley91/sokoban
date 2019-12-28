import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple

from pygame.rect import Rect

from animator import Animator
from coordinate import Coordinate
from music_player import MusicPlayer
from resources import Resources
from undo import UndoManager

if TYPE_CHECKING:
    from grid import Grid


class Piece(ABC):
    def __init__(self, grid: "Grid", undo_manager: UndoManager, animator: Animator,
                 music_player: MusicPlayer, resources: Resources):
        self.grid = grid
        self.undo_manager = undo_manager
        self.animator = animator
        self.music_player = music_player
        self.resources = resources

    @property
    def coordinate(self) -> Coordinate:
        return self.grid.get_piece_coordinate(self)

    @property
    def x(self) -> int:
        return self.coordinate.x

    @property
    def y(self) -> int:
        return self.coordinate.y

    @abstractmethod
    def draw(self, grid_offset: Tuple[int, int], square_size: int):
        pass

    def get_rect_at_coordinate(self, grid_offset: Tuple[int, int], square_size: int):
        return Rect(grid_offset[0] + (self.coordinate.x * square_size),
                    grid_offset[1] + (self.coordinate.y * square_size),
                    square_size, square_size)

    def move(self, coordinate: Coordinate) -> bool:
        """
        Move this piece onto the given coordinate.

        :param coordinate: the coordinate to move onto
        :return: False if this piece was unable to move. True otherwise.
        """
        if coordinate == self.coordinate:
            return False

        label = str(uuid.uuid4())
        self.undo_manager.save_position(label)
        for piece in self.grid[coordinate]:
            if not piece.react_to_piece_move(self):
                self.undo_manager.undo(label)
                return False

        self.grid.move_piece(self, coordinate)
        self.undo_manager.delete_label(label)
        return True

    @abstractmethod
    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Prepare for the given piece to move onto this piece's current location. This may mean
        this piece needs to move.
        :param piece: the piece moving onto this one.
        :return: True if the move was successful, and false otherwise.
        """
        pass

