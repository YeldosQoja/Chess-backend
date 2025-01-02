from typing import List
from .typing import Square, PieceType
from .move import Move
from .game.ipiece import IPiece
from .game.piece import Piece
from .game.board import Board

def is_valid_square(square: Square) -> bool:
    y, x = square
    return 0 <= y < 8 and 0 <= x < 8

def encode_square(square: Square) -> str:
    i, j = square
    rank = str(8 - i)
    file = chr(ord("a") + j)
    return file + rank

def decode_square(notation: str) -> Square:
    file, rank = list(notation)
    i = 8 - int(rank)
    j = ord(file) - ord("a")
    return (i, j)

def create_pieces_from_board(board_repr: str, strategy_factory) -> List[IPiece]:
    pieces = []
    for i, row in enumerate(board_repr.split("/")):
        j = 0
        for char in list(row):
            if char.isdigit():
                j += int(char)
            else:
                color = "white" if char.isupper() else "black"
                piece_type = char.lower()
                strategy = strategy_factory.create(piece_type)
                piece = Piece(color, (i, j), strategy)
                pieces.append(piece)
                j += 1

                if piece_type == PieceType.PAWN:
                    initial_y = 6 if color == "white" else 1
                    if i != initial_y:
                        piece.is_moved = True
    return pieces

def create_board_repr(board: Board) -> str:
    res = []
    for i in range(8):
        empty_squares = 0
        row = []
        for j in range(8):
            piece = board[i][j]
            if not piece:
                empty_squares += 1
                if j == 7:
                    row.append(str(empty_squares))
            else:
                if empty_squares > 0:
                    row.append(str(empty_squares))
                    empty_squares = 0
                piece_type = str(piece.type)
                row.append(piece_type if piece.color == "black" else piece_type.capitalize())
        res.append("".join(row))
    return "/".join(res)

def create_en_passant_target(en_passant_pawn: IPiece) -> str:
    i, j = en_passant_pawn.current_square
    color = en_passant_pawn.color
    en_passant_target_square = (i + (1 if color == "white" else -1), j)
    return encode_square(en_passant_target_square)

def find_en_passant_pawn(en_passant_target: str, pieces: List[IPiece]) -> IPiece | None:
    if en_passant_target == "-":
        return None
    i, j = decode_square(en_passant_target)
    square = (i + (-1 if i > 3 else 1), j)
    for piece in pieces:
        if piece.current_square == square:
            return piece
    return None

# def create_castling_rights(white_king)