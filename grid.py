from typing import List, Iterable, Dict, Set, TYPE_CHECKING

from animator import Animator
from coordinate import Coordinate
from music_player import MusicPlayer

from pieces.nothing import NothingPiece
from resources import Resources
from undo import UndoManager

if TYPE_CHECKING:
    from pieces.piece import Piece


class Grid:
    def __init__(self, undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer,
                 resources: Resources, width: int, height: int):
        self.__undo_manager = undo_manager
        self.__resources = resources
        self.__width = width
        self.__height = height

        # Various dictionaries for efficiency
        self.__coordinates_to_pieces: Dict[Coordinate, List["Piece"]] = dict()
        self.__pieces_to_coordinates: Dict["Piece", Coordinate] = dict()
        self.__piece_types_to_pieces: Dict[type, Set["Piece"]] = dict()

        self.__piece_types_to_pieces[NothingPiece] = set()
        for x in range(0, width):
            for y in range(0, height):
                nothing = NothingPiece(self, undo_manager, animator, music_player, resources)
                self.__coordinates_to_pieces[Coordinate(x=x, y=y)] = [nothing]
                self.__pieces_to_coordinates[nothing] = Coordinate(x=x, y=y)
                self.__piece_types_to_pieces[type(nothing)].add(nothing)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def __iter__(self) -> Iterable[Coordinate]:
        return iter(self.__coordinates_to_pieces.keys())

    def __getitem__(self, coordinate: Coordinate) -> List["Piece"]:
        self.__check_coordinate(coordinate)
        return list(self.__coordinates_to_pieces[coordinate])

    def remove_pieces(self, coordinate: Coordinate) -> None:
        """
        Remove all pieces from a coordinate on the grid
        :param coordinate: where to remove all pieces
        :return: nothing
        """
        for pieces in list(self.__coordinates_to_pieces[coordinate]):
            self.remove_piece(pieces)

    def remove_piece(self, piece: "Piece") -> None:
        """
        Remove a piece from the grid
        :param piece: the piece to remove
        :return: nothing
        """
        coordinate = self.__pieces_to_coordinates.get(piece, None)
        if coordinate:
            self.__coordinates_to_pieces[coordinate].remove(piece)
            self.__pieces_to_coordinates.pop(piece, None)

        if type(piece) in self.__piece_types_to_pieces and piece in self.__piece_types_to_pieces[type(piece)]:
            self.__piece_types_to_pieces[type(piece)].remove(piece)

        # If we actually did remove the piece, put it back on undo
        if coordinate:
            self.__undo_manager.register(lambda: self.add_piece(piece, coordinate), lambda: self.remove_piece(piece))

    def add_piece(self, piece: "Piece", coordinate: Coordinate):
        """
        Add a piece to the grid, putting it on top of any existing pieces.
        This also removes it from any existing location
        :param piece: the piece to add
        :param coordinate: where to add the piece
        :return: nothing
        """
        self.__check_coordinate(coordinate)
        self.remove_piece(piece)

        self.__coordinates_to_pieces[coordinate].append(piece)
        self.__pieces_to_coordinates[piece] = coordinate

        if not type(piece) in self.__piece_types_to_pieces:
            self.__piece_types_to_pieces[type(piece)] = set()

        self.__piece_types_to_pieces[type(piece)].add(piece)

        # If the piece did exist at a previous location, remove will have recorded an undo to put it back already
        self.__undo_manager.register(lambda: self.remove_piece(piece), lambda: self.add_piece(piece, coordinate))

    def move_piece(self, piece: "Piece", coordinate: Coordinate):
        """
        Alias for add_piece which has the effect of moving the piece if it already exists in the grid.
        :param piece: the piece to move
        :param coordinate: the new coordinate for the piece
        :return: nothing
        """
        self.add_piece(piece, coordinate)

    def get_piece_coordinate(self, piece: "Piece"):
        """
        Get the coordinates for a piece. Raises a KeyError if the piece is not in the grid.
        :param piece: the piece to get the coordinate for
        :return: the coordinate for the piece
        """
        return self.__pieces_to_coordinates[piece]

    def get_pieces_of_type(self, piece_type: type) -> Set["Piece"]:
        """
        Get all pieces of a given type
        :param piece_type: the type of piece to get
        :return: a set of all those piece types
        """
        if not piece_type in self.__piece_types_to_pieces:
            self.__piece_types_to_pieces[piece_type] = set()

        return set(self.__piece_types_to_pieces[piece_type])

    def __check_coordinate(self, coordinate: Coordinate):
        """
        Check the coordinates fall within the grid
        :param coordinate: a coordinate in (x, y)
        :return: nothing, but raises an error if the coordinate is not in the grid
        """
        x, y = coordinate
        if x < 0 or x >= self.__width:
            raise ValueError(f"x out of range: {x}")
        if y < 0 or y >= self.__height:
            raise ValueError(f"y out of range: {y}")
