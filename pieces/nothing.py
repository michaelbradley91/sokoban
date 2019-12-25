import pygame

from colours import WHITE
from pieces.piece import Piece
from resources import scale, dim


class NothingPiece(Piece):
    """
    A piece representing nothing.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        """
        Allows anything to be moved on top of it.
        """
        return True

    def draw(self, rect: pygame.Rect):
        self.resources.display.blit(scale(rect, self.resources.floor_image), rect)
