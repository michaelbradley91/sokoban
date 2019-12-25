import pygame

from colours import GREY
from pieces.piece import Piece
from resources import scale, dim


class WallPiece(Piece):
    """
    A piece representing a simple wall.
    """
    def react_to_piece_move(self, piece: "Piece") -> bool:
        return False

    def draw(self, rect: pygame.Rect):
        self.resources.display.blit(scale(rect, self.resources.wall_image), rect)
