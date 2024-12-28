from abc import ABCMeta, abstractmethod
from typing import List
from ..typing import Square
from ..move import Move

class IStrategy(metaclass=ABCMeta):
    @abstractmethod
    def get_pseudo_valid_moves(self, piece_square: Square) -> List[Square]:
        raise NotImplementedError

    @abstractmethod
    def is_move_legal(self, start_square: Square, end_square: Square) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def get_valid_moves(self, piece_square: Square) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def make_move(self, move: Move) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_valid_square(self, square: Square) -> bool:
        raise NotImplementedError

    @abstractmethod
    def should_get_promoted(self, piece_square: Square) -> bool:
        raise NotImplementedError