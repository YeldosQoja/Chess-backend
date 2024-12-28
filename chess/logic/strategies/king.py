from typing import List
from ..typing import *
from ..game.ipiece import IPiece
from .strategy import Strategy


class KingStrategy(Strategy):
    def __init__(self, game):
        super().__init__(game, PieceType.KING)

    def get_pseudo_valid_moves(self, piece_square: Square) -> List[Square]:
        rank, file = piece_square
        piece = self.game.get_piece(piece_square)
        moves = []
        for rank_offset, file_offset in HORIZONTAL_VERTICAL_OFFSETS + DIAGONAL_OFFSETS:
            square = (rank + rank_offset, file + file_offset)
            if not self.is_valid_square(square):
                continue
            enemy_piece = self.game.get_piece(square)
            if not enemy_piece or enemy_piece.color != piece.color:
                moves.append(square)
        return moves
    
    def get_valid_moves(self, piece_square):
        rank, file = piece_square
        piece = self.game.get_piece(piece_square)

        moves = super().get_valid_moves(piece_square)

        if self.is_king_side_castle_valid(piece):
            moves.append((rank, 6))
        if self.is_queen_side_castle_valid(piece):
            moves.append((rank, 2))

        return moves

    def make_move(self, move):
        start_rank, start_file = move.start_square
        _, end_file = move.end_square
        if abs(start_file - end_file) == 2:  # Castling
            if end_file == 6:
                rook = self.game.get_piece((start_rank, 7))
                if rook:
                    rook.move_to((start_rank, 5))
            elif end_file == 2:
                rook = self.game.get_piece((start_rank, 0))
                if rook:
                    rook.move_to((start_rank, 3))
        super().make_move(move)

    def is_king_side_castle_valid(self, piece: IPiece) -> bool:
        rank, file = piece.current_square
        rook = self.game.get_piece((rank, 7))
        if (
            piece.is_moved
            or not rook
            or rook.type != PieceType.ROOK
            or rook.is_moved
            or self.game.is_square_threatened(piece.current_square, piece.color)
        ):
            return False
        for i in range(file + 1, 7):
            square = (rank, i)
            is_threatened = self.game.is_square_threatened(square, piece.color)
            ally_piece = self.game.get_piece(square)
            if ally_piece or is_threatened:
                return False
        return True

    def is_queen_side_castle_valid(self, piece: IPiece) -> bool:
        rank, file = piece.current_square
        rook = self.game.get_piece((rank, 0))
        if (
            piece.is_moved
            or not rook
            or rook.type != PieceType.ROOK
            or rook.is_moved
            or self.game.is_square_threatened(piece.current_square, piece.color)
        ):
            return False
        for i in range(file - 1, 1, -1):
            square = (rank, i)
            is_threatened = self.game.is_square_threatened(square, piece.color)
            ally_piece = self.game.get_piece(square)
            if ally_piece or is_threatened:
                return False
        return True
