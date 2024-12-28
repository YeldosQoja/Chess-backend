from ..typing import PieceType
from .strategy import Strategy

class PawnStrategy(Strategy):
    def __init__(self, game):
        super().__init__(game, PieceType.PAWN)

    def get_pseudo_valid_moves(self, piece_square):
        piece = self.game.get_piece(piece_square)
        rank, file = piece_square
        rank_offset = -1 if piece.color == "white" else 1
        
        moves = []

        # if there is no piece in front of pawn
        square = (rank + rank_offset, file)
        if self.is_valid_square(square) and not self.game.get_piece(square):
            moves.append(square)
            # if pawn has not moved yet
            square = (rank + rank_offset * 2, file)
            if not piece.is_moved and not self.game.get_piece(square):
                moves.append(square)

        # Diagonal Captures
        for file_offset in [-1, 1]:
            square = (rank + rank_offset, file + file_offset)
            enemy_piece = self.game.get_piece(square)
            if enemy_piece and enemy_piece.color != piece.color:
                moves.append(square)

        # En passant captures
        for file_offset in [-1, 1]:
            square = (rank, file + file_offset)
            enemy_piece = self.game.get_piece(square)
            if (
                enemy_piece
                and enemy_piece.color != piece.color
                and self.game.current_en_passant_pawn == enemy_piece
            ):
                moves.append((rank + rank_offset, file + file_offset))

        return moves
    
    def make_move(self, move):
        piece = self.game.get_piece(move.start_square)
        start_rank, start_file = move.start_square
        end_rank, end_file = move.end_square

        if not piece.is_moved and abs(end_rank - start_rank) == 2:
            self.game.current_en_passant_pawn = piece
        elif self.game.current_en_passant_pawn and self.game.current_en_passant_pawn.color != piece.color:
            i, j = self.game.current_en_passant_pawn.current_square
            en_passant_target_square = (i + (-1 if piece.color == "white" else 1), j)
            if move.end_square == en_passant_target_square:
                self.game.current_en_passant_pawn.is_captured = True
        
        super().make_move(move)
        
    def should_get_promoted(self, piece_square):
        piece = self.game.get_piece(piece_square)
        rank, _ = piece_square
        promotion_rank = 0 if piece.color == "white" else 7
        return rank == promotion_rank
