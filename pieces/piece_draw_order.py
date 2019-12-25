from pieces.crate import CratePiece
from pieces.goal import GoalPiece
from pieces.nothing import NothingPiece
from pieces.player import PlayerPiece
from pieces.wall import WallPiece

PIECE_DRAW_ORDER = [NothingPiece, GoalPiece, WallPiece, CratePiece, PlayerPiece]
