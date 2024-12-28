from typing import List, Tuple
from .strategy import Strategy

class DirectionalMoverStrategy(Strategy):
    def __init__(self, game, piece_type, movement_offsets: List[Tuple[int, int]]):
        super().__init__(game, piece_type)
        self.movement_offsets = movement_offsets

    def get_pseudo_valid_moves(self, piece_square):
        rank, file = piece_square
        piece = self.game.get_piece(piece_square)
        moves = []
        for rank_offset, file_offset in self.movement_offsets:
            curr_rank, curr_file = (rank + rank_offset, file + file_offset)
            square = (curr_rank, curr_file)
            while self.is_valid_square(square):
                enemy_piece = self.game.get_piece(square)
                if enemy_piece and piece.color == enemy_piece.color:
                    break
                else:
                    moves.append(square)
                    if not enemy_piece:
                        curr_rank += rank_offset
                        curr_file += file_offset
                        square = (curr_rank, curr_file)
                    else:
                        break
        return moves
