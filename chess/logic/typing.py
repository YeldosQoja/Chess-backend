from typing import Tuple
from enum import StrEnum

Square = Tuple[int, int]

class PieceType(StrEnum):
    PAWN = "p"
    ROOK = "r"
    KNIGHT = "n"
    BISHOP = "b"
    QUEEN = "q"
    KING = "k"


HORIZONTAL_VERTICAL_OFFSETS = [
    (-1, 0),  # Up
    (0, 1),  # Right
    (1, 0),  # Down
    (0, -1),  # Left
]

DIAGONAL_OFFSETS = [
    (-1, -1),  # Top-left
    (-1, 1),  # Top-right
    (1, 1),  # Bottom-right
    (1, -1),  # Bottom-left
]

KNIGHT_OFFSETS = [
    (-1, -2),  # Up 1, Left 2
    (-2, -1),  # Up 2, Left 1
    (-2, 1),  # Up 2, Right 1
    (-1, 2),  # Up 1, Right 2
    (1, 2),  # Down 1, Right 2
    (2, 1),  # Down 2, Right 1
    (2, -1),  # Down 2, Left 1
    (1, -2),  # Down 1, Left 2
]
