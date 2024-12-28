from ..typing import Square, PieceType
from ..move import Move
from ..strategies.istrategy import IStrategy
from .ipiece import IPiece

class Piece(IPiece):
    def __init__(self, color: str, square: Square, strategy: IStrategy):
        self.color = color
        self.current_square = square
        self.strategy = strategy
        self.is_captured = False
        self.is_moved = False

    @property
    def type(self) -> PieceType:
        return self.strategy.type

    def get_valid_moves(self):
        return self.strategy.get_valid_moves(self.current_square)

    def move_to(self, square):
        self.strategy.make_move(Move(self.current_square, square))

    def update_strategy(self, strategy):
        self.strategy = strategy
    
    def is_move_valid(self, square: Square):
        valid_moves = self.get_valid_moves()
        return any([move == square for move in valid_moves])
    
    def is_move_pseudo_valid(self, square: Square):
        pseudo_valid_moves = self.strategy.get_pseudo_valid_moves(self.current_square)
        return any([move == square for move in pseudo_valid_moves])
    
    def should_get_promoted(self):
        return self.strategy.should_get_promoted(self.current_square)
