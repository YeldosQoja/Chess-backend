from .typing import Square

class Move:
    def __init__(self, start_square: Square, end_square: Square):
        self.start_square = start_square
        self.end_square = end_square