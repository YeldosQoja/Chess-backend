from ..typing import PieceType, DIAGONAL_OFFSETS
from ..game.ichess import IChess
from .directional_mover import DirectionalMoverStrategy

class BishopStrategy(DirectionalMoverStrategy):
    def __init__(self, game: IChess):
        super().__init__(game, PieceType.BISHOP, DIAGONAL_OFFSETS)
