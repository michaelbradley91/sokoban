from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.static import StaticPiece
from pieces.floor import FloorPiece
from pieces.player import PlayerPiece
from pieces.wall import WallPiece

PIECE_DRAW_ORDER = [FloorPiece, GoalPiece, WallPiece, CratePiece, PlayerPiece, StaticPiece]
