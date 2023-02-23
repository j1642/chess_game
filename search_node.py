class SearchNode():
    def __init__(self, chessboard, depth, move=None):
        self.chessboard = chessboard
        self.subnodes = []
        self.depth = depth
        self.move = move
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
            self.chessboard.update_black_controlled_squares()
            self.chessboard.remove_illegal_moves_for_pinned_pieces('white')
            self.chessboard.update_black_controlled_squares()
            self.chessboard.white_king.update_moves(self.chessboard)
        elif self.to_move == 'black':
            self.chessboard.update_black_controlled_squares()
            self.chessboard.update_white_controlled_squares()
            self.chessboard.remove_illegal_moves_for_pinned_pieces('black')
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
                self.subnodes.append(
                    SearchNode(self.chessboard, self.depth - 1, move=move))
                # Undo the move.
                piece.square = orig_piece_square
                self.chessboard.squares[orig_piece_square] = piece
                self.chessboard.squares[move] = orig_occupant
                try:
                    if orig_occupant.color == 'white':
                        try:
                            # Where is this bug coming from?
                            assert orig_occupant \
                                not in self.chessboard.white_pieces
                            self.chessboard.white_pieces.insert(
                                0,
                                orig_occupant)
                        except AssertionError:
                            pass
                    elif orig_occupant.color == 'black':
                        try:
                            assert orig_occupant \
                                not in self.chessboard.black_pieces
                            self.chessboard.black_pieces.insert(
                                0,
                                orig_occupant)
                        except AssertionError:
                            pass
                except AttributeError:
                    pass
                self.chessboard.last_move_piece = prev_last_move_piece
                self.chessboard.last_move_from_to = prev_last_move_from_to
                if switch_piece_has_moved_to_false:
                    piece.has_moved = False


if __name__ == '__main__':
    import unittest

    import chess_utilities
    import engine

    def nega_max(root, depth):
        """Recursive depth-first search of the search tree."""
        if depth == 0:
            return engine.evaluate_position(root.chessboard), \
                    root.move
        max_score = -1000000
        for subnode in root.subnodes:
            raw_score, raw_move = nega_max(subnode, depth - 1)
            score = -1 * raw_score
            if score > max_score:
                max_score = score
                move = raw_move
        return max_score, move


    class TestSearchNode(unittest.TestCase):
        def test_search(self):
            chessboard = chess_utilities.import_fen_to_board(
                'k7/8/8/8/6rR/8/8/K7 w')
            chessboard.update_white_controlled_squares()
            chessboard.update_black_controlled_squares()
            chessboard.white_king.update_moves(chessboard)
            root = SearchNode(chessboard, 2)
            print(nega_max(root, 2))


    unittest.main()
