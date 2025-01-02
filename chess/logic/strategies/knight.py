from ..typing import PieceType, KNIGHT_OFFSETS
from ..utility import is_valid_square
from .strategy import Strategy

class KnightStrategy(Strategy):
    def __init__(self, game):
        super().__init__(game, PieceType.KNIGHT)

    def get_pseudo_valid_moves(self, piece_square):
        piece = self.game.get_piece(piece_square)
        rank, file = piece_square
        moves = []
        for rank_offset, file_offset in KNIGHT_OFFSETS:
            square = (rank + rank_offset, file + file_offset)
            if not is_valid_square(square):
                continue
            enemy_piece = self.game.get_piece(square)
            if not enemy_piece or enemy_piece.color != piece.color:
                moves.append(square)
        return moves
