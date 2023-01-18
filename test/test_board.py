"""All tests for board.py."""

# from os import chdir, getcwd
# if getcwd().split('/')[-1] != 'chess':
#    chdir('..')
import pickle
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

        Note that the king is in double check here. Double check is already
        accounted for in the code.
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
        chessboard = board.Board()
        white_king = pieces.King('K', 'white', 4)
        black_rook_a = pieces.Rook('ra', 'black', 0)
        black_rook_h = pieces.Rook('rh', 'black', 7)
        black_queen = pieces.Queen('q', 'black', 60)
        black_king = pieces.King('k', 'black', 63)

        chessboard.white_king = white_king
        chessboard.black_king = black_king
        chessboard.last_move_piece = black_rook_a
        chessboard.white_pieces = [white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h, black_queen,
                                   black_king]

        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()

        checking_pieces = chessboard.find_checking_pieces()
        self.assertEqual(checking_pieces, chessboard.black_pieces[:-1])

    def test_why_assertion_error_triggers_in_find_checking_pieces(self):
        """Test Causes:
        1. chess_utilities.import_fen_to_board had bug where
           Board.last_piece_move is always the wrong color, leading to
           the incorrect king being selected as checked_king in
           Board.find_checking_pieces.

        2. In Board.find_checking_pieces, the checked_square is not in
           opponent_controlled_squares because Board.squares[52] == ' '
           instead of the checked king object.

           The "invisible" king in King.update_moves is undetected by
           the pawn which is checking the king.

           This bug has only appeared when a pawn is checking the king.
           It may have also been bugged when a knight is checking the
           king.

        Fix: Call Board.find_checking_pieces immediately upon learning
           a king is in check (in King.update_moves). Later on, add
           the checked king's square to the moves list of each of the
           checking pieces.
        """
        position = 'rnbq1b1r/ppppkppp/5P2/6B1/5P2/6P1/PPP1P2P/RN1QKBNR b'
        chessboard = chess_utilities.import_fen_to_board(position)

        chessboard.last_move_from_to = (36, 45)
        chessboard.update_white_controlled_squares()

        self.assertTrue(52 in chessboard.white_controlled_squares)
        self.assertEqual(chessboard.black_king, chessboard.squares[52])
        chessboard.update_black_controlled_squares()

        # Alternative plan: if piece type is pawn, do not update moves if
        # opponent king is in check (b/c pawn does not attack unlimited
        # distances).

    def test_fix_assertion_error_in_find_checking_pieces_again(self):
        """AssertionError: checked_square not in opponent_controlled_squares.

        Bugs:
            1. Pawn forward moves treated as attacking moves which block
            opponent king movement.

            2. Pawn diagonal captures do not prevent king from moving into
            check there.

        Fixed: Bug 1 above in pieces.Pawn. Bug 2 is not ocurring, perhaps due
        to the entire code running without inturruption due to an error.

        Same assertion error as in the test above.
        """
        position = 'r2q3r/p2pkP1p/b1p2P1b/1B3p1Q/1P3P2/4P3/PP5P/R1B1K1NR b'
        # position_from_log =
        # 'r2q3r/p2pkP1p/b1p2P2/1B3p1Q/1P3b2/4P3/PP5P/R1B1K1NR w'

        chessboard = chess_utilities.import_fen_to_board(position)
        # print('\n')
        # print(chessboard)
        # print('\n')
        # print(chess_utilities.import_fen_to_board(position_from_log))

        chessboard.last_move_piece = chessboard.squares[45]
        chessboard.last_move_from_to = (36, 45)

        chessboard.squares[53].has_moved = True
        chessboard.update_white_controlled_squares()

        self.assertTrue(52 in chessboard.white_controlled_squares)
        self.assertEqual(chessboard.black_king, chessboard.squares[52])

        chessboard.update_black_controlled_squares()
        self.assertTrue(chessboard.black_king.in_check)
        chessboard.black_king.update_moves(chessboard)
        # print(chessboard.black_king.moves)

        self.assertEqual(set(chessboard.black_king.moves),
                         set([61, 43, 44, 45]))

        chessboard.white_king.update_moves(chessboard)
        chessboard.black_king.update_moves(chessboard)

    def test_fix_assertion_error_when_king_is_checked(self):
        """When error occurred, 'BLACK loses by checkmate' was printed to
        standard output, indicating that len(checking_pieces) was more than 1.

        Fixes: 1. (May not help but is a code improvement. There likely is a
                   better way to accomplish the same change.)
                  In board.moves_must_escape_check_or_checkmate(),
                  escape call stack immediately with sys.exit() instead of
                  finishing King.update_moves(), etc.
        """
        db_row = chess_utilities.load_board_from_db(row_id=16)
        row_id, _, error_type, error_value, pickled_chessboard = db_row

        self.assertEqual(row_id, 16)

        chessboard = pickle.loads(pickled_chessboard)
        # Return black A pawn to where it was during white's turn.
        chessboard.squares[24], chessboard.squares[32] = ' ', \
            chessboard.squares[24]
        print('\n')
        print(chessboard)

        self.assertEqual(chessboard.black_king.square, 52)
        self.assertTrue(52 in chessboard.white_controlled_squares)
        chessboard.last_move_piece = chessboard.squares[53]
        chessboard.last_move_from_to = (39, 53)

        chessboard.update_white_controlled_squares()
        # Next two lines cause the two pieces in checking_pieces when
        # black_king updates.
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        # checking pieces == [(Q, Sq: 53, white), \
        #                     (Pg, Sq: 44, white, has_moved: True)]
        # Pawn of 44.moves == [52], where black king is. Checking piece is
        # determined by piece.moves, not piece.protected_squares.
        chessboard.black_king.update_moves(chessboard)

# Must be removed or commented out to run tests in the terminal.
# unittest.main()
