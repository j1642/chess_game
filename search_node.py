class SearchNode():
    def __init__(self, chessboard, depth):
        self.chessboard = chessboard
        self.subnodes = []
        self.depth = depth
        self.eval = None

        if self.chessboard.last_move_piece.color == 'white':
            self.to_move = 'black'
            self.pieces_to_move = self.chessboard.black_pieces
        # White to move if Board.last_move_piece not set
        else:
            self.to_move = 'white'
            self.pieces_to_move = self.chessboard.white_pieces

        self.update_board()
        if depth > 0:
            self.make_subnodes()

    def update_board(self):
        if self.to_move == 'white':
            self.chessboard.update_white_controlled_squares()
            self.chessboard.remove_illegal_moves_for_pinned_pieces('black')
            self.chessboard.update_black_controlled_squares()
            self.chessboard.white_king.update_moves(self.chessboard)
        elif self.to_move == 'black':
            self.chessboard.update_black_controlled_squares()
            self.chessboard.remove_illegal_moves_for_pinned_pieces('white')
            self.chessboard.update_white_controlled_squares()
            self.chessboard.black_king.update_moves(self.chessboard)

    def make_subnodes(self):
        for piece in self.pieces_to_move:
            orig_piece_square = piece.square
            prev_last_move_piece = self.chessboard.last_move_piece
            prev_last_move_from_to = self.chessboard.last_move_from_to
            switch_piece_has_moved_to_false = False
            try:
                if piece.has_moved is False:
                    switch_piece_has_moved_to_false = True
            except AttributeError:
                pass
            for move in piece.moves:
                orig_occupant = self.chessboard.squares[move]
                piece.move_piece(self.chessboard, move)
                self.chessboard.last_piece_move = piece
                self.chessboard.last_move_from_to = (orig_piece_square, move)
                self.subnodes.append(
                    SearchNode(self.chessboard, self.depth - 1))
                # Undo the move.
                piece.square = orig_piece_square
                self.chessboard.squares[orig_piece_square] = piece
                self.chessboard.squares[move] = orig_occupant
                self.chessboard.last_move_piece = prev_last_move_piece
                self.chessboard.last_move_from_to = prev_last_move_from_to
                if switch_piece_has_moved_to_false:
                    piece.has_moved = False


if __name__ == '__main__':
    import unittest

    class TestSearchNode(unittest.TestCase):

        def test_(self):
            pass
