from django.test.testcases import TestCase
from chess.logic.utility import encode_square, decode_square
from chess.logic.typing import Square

class ChessUtilityTestCase(TestCase):
    def test_encode_square(self):
        square1: Square = (4, 2)
        notation1 = encode_square(square1)
        square2: Square = (0, 0)
        notation2 = encode_square(square2)
        square3: Square = (7, 7)
        notation3 = encode_square(square3)
        square4: Square = (5, 4)
        notation4 = encode_square(square4)
        self.assertEqual(notation1, "c4")
        self.assertEqual(notation2, "a8")
        self.assertEqual(notation3, "h1")
        self.assertEqual(notation4, "e3")

    def test_decode_square(self):
        notation1 = "g5"
        notation2 = "c3"
        notation3 = "g7"
        square1 = decode_square(notation1)
        square2 = decode_square(notation2)
        square3 = decode_square(notation3)
        self.assertEqual(square1, (3, 6))
        self.assertEqual(square2, (5, 2))
        self.assertEqual(square3, (1, 6))

