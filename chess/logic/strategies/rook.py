from ..typing import PieceType, HORIZONTAL_VERTICAL_OFFSETS
from .directional_mover import DirectionalMoverStrategy

class RookStrategy(DirectionalMoverStrategy):
    def __init__(self, game):
        super().__init__(game, PieceType.ROOK, HORIZONTAL_VERTICAL_OFFSETS)
