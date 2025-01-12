from .istrategy import IStrategy
from ..game.ichess import IChess
from ..typing import PieceType
from ..move import Move


class Strategy(IStrategy):
    def __init__(self, game: IChess, piece_type: PieceType):
        self.game = game
        self.type = piece_type

    def get_pseudo_valid_moves(self, piece_square):
        return []

    def _is_move_legal(self, start_square, end_square):
        start_piece = self.game.get_piece(start_square)
        end_piece = self.game.get_piece(end_square)

        is_moved = start_piece.is_moved
        self._make_move(Move(start_square, end_square))
        
        king_square = self.game.get_king_square(start_piece.color)
        is_legal = True
        if self.game.is_square_threatened(king_square, start_piece.color):
            is_legal = False
        
        self._make_move(Move(end_square, start_square))
        start_piece.is_moved = is_moved

        if end_piece:
            end_piece.is_captured = False
        
        return is_legal

    def get_valid_moves(self, piece_square):
        moves = self.get_pseudo_valid_moves(piece_square)
        return [
            end_square
            for end_square in moves
            if self._is_move_legal(piece_square, end_square)
        ]
    
    def _make_move(self, move):
        piece = self.game.get_piece(move.start_square)
        enemy_piece = self.game.get_piece(move.end_square)

        if enemy_piece:
            enemy_piece.is_captured = True

        piece.is_moved = True
        piece.current_square = move.end_square

    def make_move(self, move):
        self._make_move(move)
