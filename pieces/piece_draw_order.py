from pieces.crate import CratePiece
from pieces.floor import FloorPiece
from pieces.goal import GoalPiece
from pieces.player import PlayerPiece
from pieces.static import StaticPiece
from pieces.wall import WallPiece

PIECE_DRAW_ORDER = [FloorPiece, GoalPiece, WallPiece, CratePiece, PlayerPiece, StaticPiece]
