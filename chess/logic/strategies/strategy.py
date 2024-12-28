from .istrategy import IStrategy
from ..game.ichess import IChess
from ..typing import PieceType


class Strategy(IStrategy):
    def __init__(self, game: IChess, piece_type: PieceType):
        self.game = game
        self.type = piece_type

    def get_pseudo_valid_moves(self, piece_square):
        return []

    def is_move_legal(self, start_square, end_square):
        start_piece = self.game.get_piece(start_square)
        end_piece = self.game.get_piece(end_square)
        
        previous_en_passant_pawn = self.game.current_en_passant_pawn

        is_moved = start_piece.is_moved

        start_piece.move_to(end_square)

        king_square = self.game.get_king_square(start_piece.color)

        is_legal = True
        if self.game.is_square_threatened(king_square, start_piece.color):
            is_legal = False

        start_piece.move_to(start_square)

        if not is_moved:
            start_piece.is_moved = False
        
        if end_piece:
            end_piece.is_captured = False
        
        self.game.current_en_passant_pawn = previous_en_passant_pawn

        return is_legal

    def get_valid_moves(self, piece_square):
        piece = self.game.get_piece(piece_square)
        pawn_should_get_promoted = False
        
        for p in self.game.pieces:
            if p.color == piece.color and p.type == PieceType.PAWN and p.should_get_promoted():
                pawn_should_get_promoted = True

        moves = self.get_pseudo_valid_moves(piece_square)

        valid_moves = [
            end_square
            for end_square in moves
            if self.is_move_legal(piece_square, end_square)
            and not pawn_should_get_promoted
        ]

        return valid_moves
    
    def make_move(self, move):
        piece = self.game.get_piece(move.start_square)
        enemy_piece = self.game.get_piece(move.end_square)

        if enemy_piece:
            enemy_piece.is_captured = True
        
        piece.is_moved = True
        piece.current_square = move.end_square

    def is_valid_square(self, square):
        rank, file = square
        return 0 <= rank < 8 and 0 <= file < 8

    def should_get_promoted(self, piece_square):
        return False
