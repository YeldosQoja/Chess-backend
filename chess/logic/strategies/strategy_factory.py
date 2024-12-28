from ..typing import PieceType
from ..game.ichess import IChess
from .istrategy import IStrategy
from .pawn import PawnStrategy
from .bishop import BishopStrategy
from .rook import RookStrategy
from .knight import KnightStrategy
from .queen import QueenStrategy
from .king import KingStrategy


class StrategyFactory:
    def __init__(self, game: IChess):
        self.game = game

    def create(self, piece_type: PieceType) -> IStrategy:
        if piece_type == PieceType.KING:
            return KingStrategy(self.game)
        if piece_type == PieceType.QUEEN:
            return QueenStrategy(self.game)
        if piece_type == PieceType.KNIGHT:
            return KnightStrategy(self.game)
        if piece_type == PieceType.ROOK:
            return RookStrategy(self.game)
        if piece_type == PieceType.BISHOP:
            return BishopStrategy(self.game)
        if piece_type == PieceType.PAWN:
            return PawnStrategy(self.game)
        return Strategy(self.game, piece_type)
