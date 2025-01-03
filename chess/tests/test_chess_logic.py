from django.test.testcases import TestCase
from chess.logic.game.chess import IChess, Chess
from chess.logic.move import Move


class ChessLogicTests(TestCase):
    def test_initial_board(self):
        game = Chess()
        correct_board = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        self.assertEqual(correct_board, repr(game))

    def test_pawn_move(self):
        game: IChess = Chess()
        game.make_move(Move(start_square=(6, 6), end_square=(4, 6)))
        moved_pawn = game.get_piece((4, 6))
        correct_board = "rnbqkbnr/pppppppp/8/8/6P1/8/PPPPPP1P/RNBQKBNR b KQkq g3"
        self.assertEqual(game.current_en_passant_pawn, moved_pawn)
        self.assertEqual(correct_board, repr(game))

    def test_invalid_move(self):
        game: IChess = Chess()
        start_square = (0, 7)
        end_square = (3, 7)
        piece = game.get_piece(start_square)
        game.make_move(Move(start_square, end_square))
        correct_board = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
        self.assertEqual(str(piece.type), "r")
        self.assertEqual(correct_board, repr(game))

    def test_two_moves_in_row(self):
        game: IChess = Chess()
        game.make_move(Move(start_square=(6, 2), end_square=(4, 2)))
        game.make_move(Move(start_square=(7, 1), end_square=(5, 2)))
        moved_pawn = game.get_piece((4, 2))
        correct_board = "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3"
        self.assertEqual(game.current_en_passant_pawn, moved_pawn)
        self.assertEqual(correct_board, repr(game))
    
    def test_from_repr_contructor(self):
        board_repr = "rnbqk2r/ppppbppp/5n2/4p3/3P4/2N1BN2/PPP2PPP/R2QK2R w KQkq -"
        game = Chess.from_repr(board_repr)
        self.assertEqual(board_repr, repr(game))

    def test_king_side_castling(self):
        board_repr = "rnbqk2r/ppppbppp/5n2/4p3/3P4/2N1BN2/PPP2PPP/R2QK2R b KQkq -"
        game: IChess = Chess.from_repr(board_repr)
        game.make_move(Move((0, 4), (0, 6)))
        correct_board = "rnbq1rk1/ppppbppp/5n2/4p3/3P4/2N1BN2/PPP2PPP/R2QK2R w KQ -"
        self.assertEqual(correct_board, repr(game))

    def test_queen_side_castling(self):
        board_repr = "rnbq1rk1/ppppbppp/5n2/4p3/3P4/2N1BN2/PPP1QPPP/R3K2R w KQ -"
        game: IChess = Chess.from_repr(board_repr)
        game.make_move(Move((7, 4), (7, 2)))
        correct_board = "rnbq1rk1/ppppbppp/5n2/4p3/3P4/2N1BN2/PPP1QPPP/2KR3R b - -"
        self.assertEqual(correct_board, repr(game))

    def test_castling_when_king_in_check(self):
        board_repr = "r1bqk2r/pppp1ppp/2n2n2/4p3/1b2P1B1/3P1N2/PPP2PPP/RNBQK2R w KQkq -"
        game: IChess = Chess.from_repr(board_repr)
        self.assertTrue(game.is_in_check())
        game.make_move(Move((7, 4), (7, 6)))
        self.assertEqual(board_repr, repr(game))

    def test_castling_when_square_attacked(self):
        board_repr = "r2qkb1r/p2n1ppp/bppp1n2/3Pp3/4P3/2N2NP1/PPP2PBP/R1BQK2R w KQkq -"
        game: IChess = Chess.from_repr(board_repr)
        game.make_move(Move((7, 4), (7, 6)))
        self.assertEqual(board_repr, repr(game))

    def test_castling_when_square_attacked_2(self):
        board_repr = "r1bqk2r/ppp2ppp/2np1n2/2bp4/2B1PP2/2N2NP1/PPP3P1/R1BQK2R w KQkq -"
        game: IChess = Chess.from_repr(board_repr)
        game.make_move(Move((7, 4), (7, 6)))
        self.assertEqual(board_repr, repr(game))

    def test_checkmate(self):
        board_repr = "r1bqkb1r/pp1npppp/2pN1n2/8/3P4/8/PPP1QPPP/R1B1KBNR b KQkq -"
        game: IChess = Chess.from_repr(board_repr)
        self.assertTrue(game.is_in_checkmate())
        self.assertEqual(board_repr, repr(game))

    def test_king_avoiding_check(self):
        board_repr = "5rk1/p3np1n/2q1r2p/1p3N1Q/3B4/3P3P/P5RK/8 b - -"
        game: IChess = Chess.from_repr(board_repr)
        valid_moves = []
        for piece in game.pieces:
            if piece.color == "black":
                valid_moves.extend(piece.get_valid_moves())
        self.assertTrue(game.is_in_check())
        self.assertListEqual([(2, 6), (3, 6), (6, 6), (2, 6)], valid_moves)
    
    def test_king_avoiding_check_2(self):
        board_repr = "2Q3k1/6pp/5r1q/6N1/1P5P/6P1/5P2/6K1 b - -"
        game = Chess.from_repr(board_repr)
        valid_moves = []
        for piece in game.pieces:
            if piece.color == "black":
                valid_moves.extend(piece.get_valid_moves())
        self.assertTrue(game.is_in_check())
        self.assertListEqual([(0, 5)], valid_moves)
        game.make_move(Move((2, 5), (0, 5)))
        self.assertFalse(game.is_in_check())

    def test_king_avoiding_from_double_check(self):
        board_repr = "2r2q1k/5pp1/4p1N1/8/1bp5/5P1R/6P1/2R4K b - -"
        game = Chess.from_repr(board_repr)
        valid_moves = []
        for piece in game.pieces:
            if piece.color == "black":
                valid_moves.extend(piece.get_valid_moves())
        self.assertTrue(game.is_in_check())
        self.assertListEqual([(0, 6)], valid_moves)

    def test_en_passant_target(self):
        board_repr = "rnbqkbnr/p1pppppp/1p6/4P3/8/8/PPPP1PPP/RNBQKBNR b KQkq -"
        game = Chess.from_repr(board_repr)
        game.make_move(Move((1, 3), (3, 3)))
        self.assertEqual(game.current_en_passant_pawn.current_square, (3, 3))
        self.assertEqual("rnbqkbnr/p1p1pppp/1p6/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6", repr(game))
        game.make_move(Move((3, 4), (2, 3)))
        self.assertEqual("rnbqkbnr/p1p1pppp/1p1P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq -", repr(game))

    def test_move_algebraic_notation(self):
        game: IChess = Chess()
        move_notation = game.make_move(Move((6, 6), (5, 6)))
        self.assertEqual(move_notation, "g3")
        self.assertEqual(repr(game), "rnbqkbnr/pppppppp/8/8/8/6P1/PPPPPP1P/RNBQKBNR b KQkq -")

        move_notation = game.make_move(Move((1, 4), (3, 4)))
        self.assertEqual(move_notation, "e5")
        self.assertEqual(repr(game), "rnbqkbnr/pppp1ppp/8/4p3/8/6P1/PPPPPP1P/RNBQKBNR w KQkq e6")

        move_notation = game.make_move(Move((7, 5), (5, 7)))
        self.assertEqual(move_notation, "Bh3")
        self.assertEqual(repr(game), "rnbqkbnr/pppp1ppp/8/4p3/8/6PB/PPPPPP1P/RNBQK1NR b KQkq -")

        move_notation = game.make_move(Move((0, 3), (4, 7)))
        self.assertEqual(move_notation, "Qh4")
        self.assertEqual(repr(game), "rnb1kbnr/pppp1ppp/8/4p3/7q/6PB/PPPPPP1P/RNBQK1NR w KQkq -")

        move_notation = game.make_move(Move((5, 6), (4, 7)))
        self.assertEqual(move_notation, "xh4")
        self.assertEqual(repr(game), "rnb1kbnr/pppp1ppp/8/4p3/7P/7B/PPPPPP1P/RNBQK1NR b KQkq -")
    
    def test_special_cases_in_algebraic_notation(self):
        game = Chess.from_repr("r1bqkbnr/1ppp1ppp/p1B5/4p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -")
        move_notation = game.make_move(Move((1, 3), (2, 2)))
        self.assertEqual(move_notation, "dxc6")
        self.assertEqual(repr(game), "r1bqkbnr/1pp2ppp/p1p5/4p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq -")

        game = Chess.from_repr("rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -")
        move_notation = game.make_move(Move((7, 5), (3, 1)))
        self.assertEqual(move_notation, "Bb5+")
        self.assertEqual(repr(game), "rnbqkbnr/pp2pppp/3p4/1Bp5/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -")

        game = Chess.from_repr("r1bqk2r/1pppbppp/p1n2n2/4p3/B3P3/3P1N2/PPP2PPP/RNBQK2R w KQkq -")
        move_notation = game.make_move(Move((7, 1), (6, 3)))
        self.assertEqual(move_notation, "Nbd2")
        self.assertEqual(repr(game), "r1bqk2r/1pppbppp/p1n2n2/4p3/B3P3/3P1N2/PPPN1PPP/R1BQK2R b KQkq -")

        game = Chess.from_repr("2rq1rk1/1b2bppp/p2p1n2/npp1p3/4P3/1BPP1N2/PP3PPP/R1BQRNK1 w - -")
        move_notation = game.make_move(Move((7, 5), (6, 3)))
        self.assertEqual(move_notation, "N1d2")
        self.assertEqual(repr(game), "2rq1rk1/1b2bppp/p2p1n2/npp1p3/4P3/1BPP1N2/PP1N1PPP/R1BQR1K1 b - -")