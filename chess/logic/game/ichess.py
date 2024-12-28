from abc import ABCMeta, abstractmethod
from typing import List
from ..move import Move
from ..typing import Square
from .board import Board
from .ipiece import IPiece


class IChess(metaclass=ABCMeta):
    pieces: List[IPiece]
    active_color: str
    current_en_passant_pawn: IPiece | None

    @property
    @abstractmethod
    def board(self) -> Board:
        raise NotImplementedError

    @abstractmethod
    def create_pieces(self, player: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def make_move(self, move: Move) -> None:
        raise NotImplementedError

    @abstractmethod
    def switch_turn(self):
        raise NotImplementedError

    @abstractmethod
    def get_piece(self, square: Square) -> IPiece | None:
        raise NotImplementedError

    @abstractmethod
    def get_king_square(self, color: str) -> Square | None:
        raise NotImplementedError

    @abstractmethod    
    def get_king(self, color: str) -> IPiece:
        raise NotImplemented

    @abstractmethod
    def set_piece(self, piece: Move, square: Square) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_square_empty(self, square: Square) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_valid_square(self, square: Square) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_square_threatened(self, square: Square, color: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_in_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_in_checkmate(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_in_stalemate(self) -> bool:
        raise NotImplementedError