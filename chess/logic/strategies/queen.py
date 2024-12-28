from ..typing import PieceType, HORIZONTAL_VERTICAL_OFFSETS, DIAGONAL_OFFSETS
from .directional_mover import DirectionalMoverStrategy

class QueenStrategy(DirectionalMoverStrategy):
    def __init__(self, game):
        super().__init__(
            game, PieceType.QUEEN, HORIZONTAL_VERTICAL_OFFSETS + DIAGONAL_OFFSETS
        )

