"""All tests for board.py."""

import unittest

import board
import chess_utilities
import pieces


class TestBoard(unittest.TestCase):
    """Test: Board methods, piece movement updates Board.squares, captures
    update Board.squares, finding interposition squares blocking check, and
    identifying checking pieces.
    """

    def test_repr_and_initialize_pieces(self):
        """Test Board.__repr__() and Board.initialize_pieces()."""
        chessboard = board.Board()
        chessboard.initialize_pieces()
        self.assertEqual(len(chessboard.white_pieces),
                         len(chessboard.black_pieces))

        self.assertEqual(len(chessboard.black_pieces), 16)

        # Finally figured out how to make nice, neat multipe line strings.
        compare_to_initial_squares_repr = \
            '|r|n|b|q|k|b|n|r|\n'\
            '|p|p|p|p|p|p|p|p|\n'\
            '| | | | | | | | |\n'\
            '| | | | | | | | |\n'\
            '| | | | | | | | |\n'\
            '| | | | | | | | |\n'\
            '|P|P|P|P|P|P|P|P|\n'\
            '|R|N|B|Q|K|B|N|R|'

        self.assertEqual(chessboard.__repr__(),
                         compare_to_initial_squares_repr)

    def test_update_white_controlled_squares(self):
        """Test Board.update_white_controlled_squares, which updates and
        centralizes all white piece moves currently possible.

        Board.white_controlled_squares also includes all of the protected
        squares which white pieces are on (friendly collision).
        """
        chessboard = board.Board()
        chessboard.initialize_pieces()
        chessboard.update_white_controlled_squares()
        squares = list(range(1, 24))
        squares.remove(7)

        self.assertEqual(chessboard.white_controlled_squares, set(squares))

    def test_update_black_controlled_squares(self):
        """Test Board.update_black_controlled_squares, which updates and
        centralizes all black piece moves currently possible.

        Board.black_controlled_squares also includes all of the protected
        squares which black pieces are on (friendly collision).
        """
        chessboard = board.Board()
        chessboard.initialize_pieces()
        chessboard.update_black_controlled_squares()
        squares = list(range(40, 63))
        squares.remove(56)
        self.assertEqual(set(chessboard.black_controlled_squares),
                         set(squares))

    def test_board_updates_upon_piece_movement(self):
        """Test that Board.squares updates appropriately as pieces move."""
        chessboard = board.Board()
        chessboard.initialize_pieces()

        # Test Pawn.move_piece() updates Board object.
        test_pawn = chessboard.squares[8]
        self.assertIsInstance(test_pawn, pieces.Pawn)
        test_pawn.update_moves(chessboard)
        test_pawn.move_piece(chessboard, 16)
        self.assertEqual(chessboard.squares[8], ' ')
        self.assertIsInstance(chessboard.squares[16], pieces.Pawn)
        self.assertEqual(chessboard.squares[16], test_pawn)

        # Remove all white pawns from the board so all other white pieces
        # can move.
        chessboard.squares[16] = ' '
        # board.squares[8:] = [' '] sets the 8th item to ' ' and removes
        # all items past index 8. Neat feature.
        chessboard.squares[8:16] = [' '] * 8

        for piece in chessboard.squares[:8]:
            piece.update_moves(chessboard)

        # Test all piece types beside pawn, which was tested above.
        new_squares = (48, 18, 16, 0, 12, 23, 21, 1)
        for ind, piece in enumerate(chessboard.squares[:8]):
            old_square = piece.square
            new_square = new_squares[ind]

            piece.update_moves(chessboard)
            piece.move_piece(chessboard, new_square)

            if chessboard.squares[old_square] == piece:
                raise Exception(f'Invalid move for {piece.name}')

            self.assertEqual(chessboard.squares[old_square], ' ')
            self.assertEqual(chessboard.squares[new_square], piece)

    def test_capture_updates_board_and_piece_lists(self):
        """Test Board.squares, Board.white_pieces, and Board.black_pieces
        update when pieces are captured.
        """
        chessboard = board.Board()
        chessboard.initialize_pieces()
        self.assertEqual(len(chessboard.white_pieces),
                         len(chessboard.black_pieces))

        self.assertEqual(len(chessboard.black_pieces), 16)

        # Scandinavian Defense move and capture sequence.
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.squares[12].move_piece(chessboard, 28)

        chessboard.update_black_controlled_squares()
        chessboard.squares[51].move_piece(chessboard, 35)

        chessboard.update_white_controlled_squares()
        chessboard.squares[28].move_piece(chessboard, 35)

        self.assertEqual(len(chessboard.black_pieces), 15)
        for piece in chessboard.black_pieces:
            self.assertTrue(piece.name != 'pd')

        chessboard.update_black_controlled_squares()
        chessboard.squares[59].move_piece(chessboard, 35)

        self.assertEqual(len(chessboard.white_pieces), 15)
        for piece in chessboard.white_pieces:
            self.assertTrue(piece.name != 'Pe')

        self.assertEqual(len(chessboard.squares), 64)

    def test_find_interposition_squares_same_rank(self):
        """Find squares (in the same row) where check can be blocked.

        Note that the king is in double check here. Double check is already
        accounted for in the code.
        """
        chessboard = board.Board()
        white_rook_a = pieces.Rook('Ra', 'white', 63)
        white_rook_h = pieces.Rook('Rh', 'white', 56)
        black_king = pieces.King('k', 'black', 58)

        interpose_sqrs = chessboard.find_interposition_squares(
            [white_rook_a, white_rook_h], black_king)

        self.assertEqual(set(interpose_sqrs), set([57, 59, 60, 61, 62]))

    def test_find_interposition_squares_same_file(self):
        """Find squares (in the same column) where check can be blocked.

        Note that the king is in double check here. Double check is
        already accounted for in board.py.
        """
        chessboard = board.Board()
        white_rook_a = pieces.Rook('Ra', 'white', 0)
        white_rook_h = pieces.Rook('Rh', 'white', 24)
        black_king = pieces.King('k', 'black', 16)

        interpose_sqrs = chessboard.find_interposition_squares(
            [white_rook_a, white_rook_h], black_king)
        self.assertEqual(interpose_sqrs, [8])

    def test_find_interposition_squares_diagonal(self):
        """Find squares (in the same diagonal) where check can be blocked.

        Note that the king is in double check here. Double check is already
        accounted for in the code.
        """
        chessboard = board.Board()
        white_queen = pieces.Queen('Q', 'white', 0)
        black_king = pieces.King('k', 'black', 63)

        interpose_squares = chessboard.find_interposition_squares(
            [white_queen], black_king)

        self.assertEqual(set(interpose_squares), set(range(9, 63, 9)))

    def test_find_checking_pieces(self):
        """Pieces checking a king can be identified."""
        chessboard = chess_utilities.import_fen_to_board(
            '4q2k/8/8/8/8/8/8/r3K2r w')
        print(chess_utilities.export_board_to_fen(chessboard))

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        checking_pieces = chessboard.find_checking_pieces()
        # All except black king
        self.assertEqual(checking_pieces, chessboard.black_pieces[:-1])
        self.assertTrue(
            isinstance(chessboard.black_pieces[-1],
                       pieces.King))
