from ..typing import PieceType
from ..strategies.strategy_factory import StrategyFactory
from .ichess import IChess
from .piece import Piece
from ..utility import (
    create_pieces_from_board,
    create_board_repr,
    create_en_passant_target,
    find_en_passant_pawn,
    is_valid_square,
    encode_square,
)


class Chess(IChess):
    def __init__(self):
        self.active_color = "white"
        self.current_en_passant_pawn = None
        self.pieces = []
        self.create_pieces("white")
        self.create_pieces("black")

    @classmethod
    def from_repr(cls, repr: str) -> IChess:
        instance = cls()
        strategy_factory = StrategyFactory(instance)

        board_repr, active_color_sign, castling_rights, en_passant_target = repr.split(
            " "
        )

        instance.active_color = "white" if active_color_sign == "w" else "black"
        instance.pieces = create_pieces_from_board(board_repr, strategy_factory)
        instance.current_en_passant_pawn = find_en_passant_pawn(
            en_passant_target, instance.pieces
        )

        white_king = instance.get_king("white")
        black_king = instance.get_king("black")
        white_king.is_moved = True
        black_king.is_moved = True

        for castle in castling_rights:
            if castle == "k" or castle == "q":
                black_king.is_moved = False
            if castle == "K" or castle == "Q":
                white_king.is_moved = False

        return instance

    def __repr__(self):
        board_repr = create_board_repr(self.board)
        turn = self.active_color[0]

        en_passant_target = "-"
        if self.current_en_passant_pawn:
            en_passant_target = create_en_passant_target(self.current_en_passant_pawn)

        white_king = self.get_king("white")
        black_king = self.get_king("black")

        castling_rights = []
        if not white_king.is_moved:
            right_rook = self.get_piece((7, 7))
            if (
                right_rook
                and right_rook.type == PieceType.ROOK
                and not right_rook.is_moved
            ):
                castling_rights.append("K")
            left_rook = self.get_piece((7, 0))
            if (
                left_rook
                and left_rook.type == PieceType.ROOK
                and not left_rook.is_moved
            ):
                castling_rights.append("Q")

        if not black_king.is_moved:
            right_rook = self.get_piece((0, 7))
            if (
                right_rook
                and right_rook.type == PieceType.ROOK
                and not right_rook.is_moved
            ):
                castling_rights.append("k")
            left_rook = self.get_piece((0, 0))
            if (
                left_rook
                and left_rook.type == PieceType.ROOK
                and not left_rook.is_moved
            ):
                castling_rights.append("q")

        castling_rights = "".join(castling_rights) if castling_rights else "-"

        return " ".join([board_repr, turn, castling_rights, en_passant_target])

    @property
    def board(self):
        _board = [[None for _ in range(8)] for _ in range(8)]
        for piece in self.pieces:
            if not piece.is_captured:
                rank, file = piece.current_square
                _board[rank][file] = piece
        return _board

    def create_pieces(self, color):
        strategy_factory = StrategyFactory(self)
        pawns_rank = 6 if color == "white" else 1
        pieces_rank = 7 if color == "white" else 0
        pawn_strategy = strategy_factory.create(PieceType.PAWN)
        pieces = [
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        ]
        for i in range(8):
            strategy = strategy_factory.create(pieces[i])
            self.pieces.append(Piece(color, (pawns_rank, i), pawn_strategy))
            self.pieces.append(Piece(color, (pieces_rank, i), strategy))

    def make_move(self, move, promotion=None) -> str:
        if self.is_move_valid(move):
            encoded_move = self.encode_move(move, promotion)
            piece = self.get_piece(move.start_square)
            self.current_en_passant_pawn = None
            piece.move_to(move.end_square)
            if promotion:
                strategy = StrategyFactory(self).create(promotion)
                piece.update_strategy(strategy)
            self.switch_turn()
            sign = ""
            if self.is_in_checkmate():
                sign = "#"
            elif self.is_in_check():
                sign = "+"
            # Returns an algebraic notation of a given move
            return encoded_move + sign
        return ""

    def is_move_valid(self, move):
        start_square = move.start_square
        end_square = move.end_square
        start_piece = self.get_piece(start_square)
        end_piece = self.get_piece(end_square)
        if not start_piece or start_piece.color != self.active_color:
            return False
        if not is_valid_square(end_square):
            return False
        if end_piece and start_piece.color == end_piece.color:
            return False
        return start_piece.is_move_valid(end_square)

    def encode_move(self, move, promotion=None) -> str:
        if not self.is_move_valid(move):
            return ""

        start_piece = self.get_piece(move.start_square)
        end_piece = self.get_piece(move.end_square)

        piece_name = (
            start_piece.type.upper() if start_piece.type != PieceType.PAWN else ""
        )
        has_captured = "x" if end_piece else ""
        square_notation = encode_square(move.end_square)
        # Find the same piece who also can move to the same square
        same_piece = next(
            (
                piece
                for piece in self.pieces
                if not piece.is_captured
                and piece.color == start_piece.color
                and piece.type == start_piece.type
                and piece.is_move_valid(move.end_square)
            ),
            None,
        )
        coordinate = ""
        if same_piece:
            start_y, start_x = move.start_square
            y, x = same_piece.current_square
            coordinate = start_y if start_x == x else start_x
        promotion_piece_name = promotion.upper() if promotion else ""

        return "".join(
            [
                piece_name,
                has_captured,
                str(coordinate),
                square_notation,
                promotion_piece_name,
            ]
        )

    def switch_turn(self):
        self.active_color = "black" if self.active_color == "white" else "white"

    def get_piece(self, square):
        rank, file = square
        if not is_valid_square(square):
            return None
        return self.board[rank][file]

    def get_king_square(self, color: str):
        for i in range(8):
            for j in range(8):
                piece = self.get_piece((i, j))
                if piece and piece.color == color and piece.type == PieceType.KING:
                    return (i, j)
        return None

    def get_king(self, color):
        square = self.get_king_square(color)
        return self.get_piece(square)

    def set_piece(self, piece, square):
        if not is_valid_square(piece):
            return IndexError()
        rank, file = square
        self.board[rank][file] = piece

    def is_square_threatened(self, square, color):
        for rank in range(8):
            for file in range(8):
                enemy_piece = self.get_piece((rank, file))
                if (
                    enemy_piece
                    and enemy_piece.color != color
                    and enemy_piece.is_move_pseudo_valid(square)
                ):
                    return True
        return False

    def is_in_check(self):
        king_square = self.get_king_square(self.active_color)
        return self.is_square_threatened(king_square, self.active_color)

    def is_in_checkmate(self):
        return self.is_in_check() and self.is_in_stalemate()

    def is_in_stalemate(self):
        for i in range(8):
            for j in range(8):
                piece = self.get_piece((i, j))
                if (
                    piece
                    and piece.color == self.active_color
                    and piece.get_valid_moves()
                ):
                    return False
        return True
