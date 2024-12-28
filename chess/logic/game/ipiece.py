from abc import ABCMeta, abstractmethod
from typing import List
from ..typing import Square, PieceType
from ..strategies.istrategy import IStrategy

class IPiece(metaclass=ABCMeta):
    color: str
    current_square: Square
    strategy: IStrategy
    is_captured: bool
    is_moved: bool

    @property
    @abstractmethod
    def type(self) -> PieceType:
        raise NotImplementedError

    @abstractmethod
    def get_valid_moves(self) -> List[Square]:
        raise NotImplementedError
    
    @abstractmethod
    def move_to(self, square: Square) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def update_strategy(self, strategy: IStrategy) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_move_valid(self, square: Square) -> bool:
        raise NotImplementedError

    @abstractmethod
    def should_get_promoted(self) -> bool:
        raise NotImplementedError