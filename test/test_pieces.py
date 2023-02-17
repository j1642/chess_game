"""All tests for the pieces.py file."""

import unittest
from unittest import mock

import board
import chess_utilities
import pieces


# It seems like there needs to be a global board variable for these tests.
# Shouldn't a local all_squares variable work without giving a NameError?
class SetUpTearDown(unittest.TestCase):
    """Instantiate and remove variables for each test."""

    def setUp(self):
        """Assign new variables for each test."""
        global chessboard
        chessboard = board.Board()
        global all_squares
        all_squares = chessboard.squares

    def tearDown(self):
        """Remove variables used in previous test."""
        global chessboard
        del chessboard
        global all_squares
        del all_squares


class TestPieces(SetUpTearDown):
    """All pieces.py tests."""

    def test_board_updates_upon_piece_movement(self):
        """The board_obj.squares array must update whenever a piece moves.
        The relevant code is in the move_piece method of each piece class.
        """
        self.assertEqual(all_squares, [' '] * 64)
        pawn = pieces.Pawn('P', 'white', 0)
        knight = pieces.Knight('N', 'white', 1)
        king = pieces.King('K', 'white', 2)
        rook = pieces.Rook('Ra', 'white', 3)
        queen = pieces.Queen('Q', 'white', 4)
        bishop = pieces.Bishop('B', 'white', 5)
        white_pieces = (pawn, knight, rook, queen, bishop, king)
        for ind, piece in enumerate(white_pieces):
            chessboard.squares[ind] = piece

        self.assertEqual(all_squares[:6], list(white_pieces))

        for piece in white_pieces:
            piece.update_moves(chessboard)

        # Make sure it is possible to iteratively update the move lists.
        self.assertEqual(pawn.moves, [8, 16])

        new_squares = (8, 18, 11, 12, 14, 10)
        for ind, piece in enumerate(white_pieces):
            piece.move_piece(chessboard, new_squares[ind])

        # This test will fail if the new_squares are changed, so it works.
        for ind, piece in enumerate(white_pieces):
            self.assertEqual(all_squares[new_squares[ind]], piece)

    def test_pawn_movement(self):
        """Pawns can move forward by one or two squares on their first move.
        Afterwards, pawns may only move forward by one squre. They may also
        capture diagonally at any point.
        """
        pawn = pieces.Pawn('Pa', 'white', 8)
        self.assertFalse(pawn.moves)
        self.assertFalse(pawn.has_moved)
        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [16, 24])

        pawn.move_piece(chessboard, 24)
        self.assertEqual(pawn.square, 24)
        self.assertEqual(chessboard.squares[24], pawn)
        self.assertTrue(pawn.has_moved)

        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [32])

        pawn = pieces.Pawn('ph', 'black', 49)
        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [41, 33])

    def test_blocked_pawn_cannot_move_forward_by_one(self):
        """A completely blocked pawn cannot move forward at all."""
        pawn = pieces.Pawn('Pa', 'white', 16)
        all_squares[16] = pawn

        # Friendly blocking piece.
        blocking_piece = pieces.Pawn('Pb', 'white', 24)
        all_squares[24] = blocking_piece
        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [])

        # Opponent blocking piece.
        blocking_piece = pieces.Pawn('q', 'black', 24)
        all_squares[24] = blocking_piece
        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [])

    def test_partially_blocked_pawn_cannot_move_forward_by_two(self):
        """A partially blocked pawn may only initially move forward by one
        square instead of one or two.
        """
        pawn = pieces.Pawn('Pa', 'white', 16)
        all_squares[16] = pawn
        self.assertFalse(pawn.has_moved)
        blocking_piece = pieces.King('k', 'black', 32)
        all_squares[32] = blocking_piece

        pawn.update_moves(chessboard)
        self.assertEqual(pawn.moves, [24])

    def test_white_pawn_captures(self):
        """White pawns can capture black pieces, can initally move forward by
        two squares, when not blocked, and cannot capture friendly pieces.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/2B1p3/3P4/8 w')
        pawn = pieces.Pawn('Pd', 'white', 11)
        pawn.update_moves(chessboard)
        self.assertFalse(pawn.has_moved)
        self.assertEqual(set(pawn.moves), set([19, 27, 20]))

    def test_black_pawn_captures(self):
        """Black pawns can capture white pieces and cannot move forward
        two squares when blocked by a friendly piece.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/p7/1Q6/n7/8/8/8/8 w')
        pawn = chessboard.squares[48]
        pawn.update_moves(chessboard)
        self.assertFalse(pawn.has_moved)
        self.assertEqual(set(pawn.moves), set([40, 41]))

    def test_pawn_cannot_capture_past_board_edge(self):
        """Opposing pawns in the A file and H file should not be able to
        capture each other.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/1p6/P6p/8 w')
        pawn = chessboard.squares[8]
        black_pawn_b = chessboard.squares[17]
        black_pawn_h = chessboard.squares[15]
        black_pawn_b.has_moved = True
        black_pawn_h.has_moved = True

        pawn.update_moves(chessboard)
        black_pawn_b.update_moves(chessboard)
        black_pawn_h.update_moves(chessboard)

        self.assertFalse(pawn.has_moved)
        self.assertTrue(black_pawn_b.has_moved)
        self.assertTrue(black_pawn_h.has_moved)

        self.assertEqual(set(pawn.moves), set([16, 24, 17]))
        self.assertEqual(set(black_pawn_b.moves), set([9, 8]))
        self.assertEqual(black_pawn_h.moves, [7])

    @mock.patch('pieces.input', create=True)
    def test_promote_pawn_walking_down_board(self, mocked_input):
        """Pawns which walk into their final rank are promoted."""
        mocked_input.side_effect = ['rook', 'knight']
        white_pawn = pieces.Pawn('Pa', 'white', 8)
        black_pawn = pieces.Pawn('ph', 'black', 63)
        chessboard.white_pieces = [white_pawn]
        chessboard.black_pieces = [black_pawn]

        while white_pawn.square < 56:
            white_pawn.update_moves(chessboard)
            white_pawn.move_piece(chessboard, white_pawn.moves[0])
        while black_pawn.square > 7:
            black_pawn.update_moves(chessboard)
            black_pawn.move_piece(chessboard, black_pawn.moves[0])

        white_pawn.update_moves(chessboard)
        black_pawn.update_moves(chessboard)

        self.assertTrue(isinstance(chessboard.squares[56], pieces.Rook))
        self.assertEqual(chessboard.white_pieces, [chessboard.squares[56]])

        self.assertTrue(isinstance(chessboard.squares[7], pieces.Knight))
        self.assertEqual(chessboard.black_pieces, [chessboard.squares[7]])

    @mock.patch('pieces.input', create=True)
    def test_promote_pawn_after_capture(self, mocked_input):
        """Pawns which just captured a piece on the promotion rank are
        promoted.
        """
        mocked_input.side_effect = ['bishop', 'rook']
        chessboard = chess_utilities.import_fen_to_board(
            '1n6/P7/8/8/8/8/p7/1N6 w')
        white_pawn = chessboard.squares[48]
        black_pawn = chessboard.squares[8]
        white_pawn.has_moved = True
        black_pawn.has_moved = True

        white_pawn.update_moves(chessboard)
        black_pawn.update_moves(chessboard)
        self.assertEqual(set(white_pawn.moves), set([56, 57]))
        self.assertEqual(set(black_pawn.moves), set([0, 1]))

        white_pawn.move_piece(chessboard, 57)
        black_pawn.move_piece(chessboard, 1)

        white_pawn.update_moves(chessboard)
        black_pawn.update_moves(chessboard)

        self.assertTrue(isinstance(chessboard.squares[57], pieces.Bishop))
        self.assertTrue(isinstance(chessboard.squares[1], pieces.Rook))

    def test_knight_movement(self):
        """Knight can move in 8 directions when not near the board edge."""
        knight = pieces.Knight('Nb', 'white', 1)
        self.assertFalse(knight.moves)

        knight.update_moves(chessboard)
        self.assertEqual(set(knight.moves), set((16, 18, 11)))

        knight.move_piece(chessboard, 18)
        self.assertEqual(knight.square, 18)

        knight.update_moves(chessboard)
        knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
        supposed_knight_moves = [(18 + i) for i in knight_move_directions]
        self.assertEqual(set(knight.moves), set((supposed_knight_moves)))

    def test_knight_friendly_piece_collision(self):
        """Knight cannot move to squares occupied by friendly pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/4P3/6N1 w')
        knight = chessboard.squares[6]
        knight.update_moves(chessboard)
        self.assertEqual(set(knight.moves), set([21, 23]))

    def test_knight_capture_available(self):
        """Knight must be able to capture opposing pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/7p/8/6N1 w')
        knight = chessboard.squares[6]
        knight.update_moves(chessboard)
        self.assertEqual(set(knight.moves), set([21, 23, 12]))

    def test_bishop_movement(self):
        """Bishop can move in 4 directions diagonally."""
        bishop = pieces.Bishop('Bc', 'white', 2)
        self.assertFalse(bishop.moves)
        bishop.update_moves(chessboard)
        supposed_bishop_moves = set((11, 20, 29, 38, 47, 9, 16))
        self.assertEqual(set(bishop.moves), supposed_bishop_moves)

        bishop = pieces.Bishop('bf', 'black', 52)
        bishop.update_moves(chessboard)
        supposed_bishop_moves = set((61, 59, 45, 38, 31, 43, 34, 25, 16))
        self.assertEqual(set(bishop.moves), supposed_bishop_moves)

        # This block should prevent bishop edge cases on the corners/sides
        bishop = pieces.Bishop('Bc', 'white', 0)
        bishop.update_moves(chessboard)
        self.assertEqual(set(bishop.moves), set(range(9, 64, 9)))

    def test_bishop_friendly_piece_collision(self):
        """Bishop cannot move into nor past friendly pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/3R4/8/8/8/7B w')
        bishop = chessboard.squares[7]
        bishop.update_moves(chessboard)
        self.assertEqual(bishop.moves, [14, 21, 28])

    def test_bishop_opponent_piece_collision(self):
        """Bishop can move into but not past opposing pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/3p4/8/8/8/7B w')
        bishop = chessboard.squares[7]
        bishop.update_moves(chessboard)
        self.assertEqual(bishop.moves, [14, 21, 28, 35])

    def test_rook_movement(self):
        """Rook can move in the 4 orthogonal directions."""
        rook = pieces.Rook('Ra', 'white', 9)
        self.assertFalse(rook.moves)
        self.assertFalse(rook.has_moved)
        rook.update_moves(chessboard)
        supposed_rook_moves = ([1, 8]
                               + list(range(17, 58, 8))
                               + list(range(10, 16)))
        self.assertEqual(set(rook.moves), set(supposed_rook_moves))
        rook.move_piece(chessboard, 10)
        self.assertTrue(rook.has_moved)

        rook = pieces.Rook('Ra', 'white', 0)
        rook.move_piece(chessboard, 3, castling=True)
        self.assertEqual(rook.square, 3)

        rook = pieces.Rook('ra', 'black', 56)
        rook.move_piece(chessboard, 59, castling=True)
        self.assertEqual(rook.square, 59)
        self.assertRaises(Exception, rook.move_piece, 59, castling=True)

        rook = pieces.Rook('Ra', 'white', 0)
        self.assertRaises(Exception, rook.move_piece, 100, castling=True)

    def test_rook_movement_edge_cases_from_corner(self):
        """Rook movement cannot wrap around the board.
        E.g. moving from square h1 to a2.
        """
        rook = pieces.Rook('Ra', 'white', 0)
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set(list(range(8, 57, 8))
                                              + list(range(1, 8))))
        rook = pieces.Rook('Rh', 'white', 7)
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set(list(range(15, 64, 8))
                                              + list(range(0, 7))))
        rook = pieces.Rook('ra', 'black', 56)
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set(list(range(0, 49, 8))
                                              + list(range(57, 64))))
        rook = pieces.Rook('rh', 'black', 63)
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set(list(range(7, 56, 8))
                                              + list(range(56, 63))))

    def test_rook_friendly_piece_collision(self):
        """Rook cannot move into or past friendly pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '1n6/8/8/8/8/8/prp5/8 w')
        rook = chessboard.squares[9]
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set([1] + list(range(17, 50, 8))))

    def test_rook_opponent_piece_collision(self):
        """Rook can move into but not past opposing pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/RrP5/1N6 w')
        rook = chessboard.squares[9]
        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves),
                         set([8, 1, 10] + list(range(17, 58, 8))))

    def test_queen_movement(self):
        """Queen must be able to move in all eight directions."""
        queen = pieces.Queen('Q', 'white', 9)
        self.assertFalse(queen.moves)
        queen.update_moves(chessboard)
        supposed_queen_moves = ([1, 8]
                                + list(range(17, 58, 8))
                                + list(range(10, 16))
                                + [0, 16, 2, 18, 27, 36, 45, 54, 63])
        self.assertEqual(set(queen.moves), set(supposed_queen_moves))

        # Queen edge cases on the corners/sides.
        queen = pieces.Queen('Q', 'white', 0)
        queen.update_moves(chessboard)
        self.assertEqual(set(queen.moves),
                         set(list(range(9, 64, 9))
                             + list(range(8, 57, 8))
                             + list(range(1, 8))))

    def test_queen_friendly_piece_collision(self):
        """Queen cannot move into or past friendly pieces."""
        chessboard = chess_utilities.import_fen_to_board(
            'qn6/1p6/8/8/8/8/8/8 w')
        queen = chessboard.squares[56]

        queen.update_moves(chessboard)
        self.assertEqual(set(queen.moves), set(range(0, 49, 8)))

    def test_queen_opponent_piece_collision(self):
        """Queen cannot move through opposing pieces but can move into
        their square.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/1P6/q1B5 w')
        queen = chessboard.squares[0]

        queen.update_moves(chessboard)
        self.assertEqual(set(queen.moves),
                         set([1, 2, 9] + list(range(8, 57, 8))))

    def test_king_movement(self):
        """Test simple parts of King.update_moves() and King.move_piece.
        This does not test castling.
        """
        king = pieces.King('k', 'black', 63)
        self.assertFalse(king.has_moved)
        self.assertFalse(king.moves)
        king.update_moves(chessboard)
        self.assertEqual(set(king.moves), set((62, 55, 54)))
        king.move_piece(chessboard, 55)
        self.assertTrue(king.has_moved)

        king = pieces.King('K', 'white', 4)
        self.assertFalse(king.moves)
        self.assertFalse(king.has_moved)
        king.update_moves(chessboard)
        self.assertEqual(set(king.moves), set((3, 11, 12, 13, 5)))

    def test_king_castling_also_moves_rook(self):
        """King castling must also move the appropriate rook."""
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/8/8/8/8/8/8/R3K2R w')
        white_king = chessboard.white_king
        white_rook_a = chessboard.squares[0]
        white_rook_h = chessboard.squares[7]
        white_rook_a.name = 'Ra'
        white_rook_h.name = 'Rh'

        black_king = chessboard.black_king
        black_rook_a = chessboard.squares[56]
        black_rook_h = chessboard.squares[63]
        black_rook_a.name = 'ra'
        black_rook_h.name = 'rh'

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertEqual(set(white_king.moves), set([3, 5, 11, 12, 13, 2, 6]))
        self.assertEqual(set(black_king.moves),
                         set([59, 61, 51, 52, 53, 58, 62]))

        white_king.move_piece(chessboard, 2)
        self.assertEqual(chessboard.squares[2], white_king)
        self.assertEqual(chessboard.squares[3], white_rook_a)
        self.assertTrue(white_king.has_moved)
        self.assertTrue(white_rook_a.has_moved)

        black_king.move_piece(chessboard, 62)
        self.assertEqual(chessboard.squares[62], black_king)
        self.assertEqual(chessboard.squares[61], black_rook_h)
        self.assertTrue(black_king.has_moved)
        self.assertTrue(black_rook_h.has_moved)

    def test_king_friendly_piece_collision(self):
        """King cannot move into friendly pieces."""
        # Technically, we should set king.has_moved to true.
        # If not doing that affects the outcome of this test, then there
        # is a bug.
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/4P3/8/3PKP2/3Q1B2 w')

        chessboard.white_king.update_moves(chessboard)
        self.assertEqual(set(chessboard.white_king.moves),
                         set([4, 19, 20, 21]))

    def test_remove_moves_to_attacked_squares(self):
        """Remove king moves into attacked squares."""
        chessboard = chess_utilities.import_fen_to_board(
            '3r1r2/8/8/8/8/4k3/8/4K3 w')
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        self.assertEqual(chessboard.white_king.moves, [])
        self.assertEqual(set(chessboard.black_king.moves),
                         set([19, 21, 28, 27, 29]))

    def test_check_if_in_check(self):
        """King.check_if_in_check() method changes King.in_check to True."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/8/r3K3 w')
        self.assertFalse(chessboard.white_king.in_check)

        chessboard.update_black_controlled_squares()
        chessboard.update_white_controlled_squares()
        self.assertTrue(chessboard.white_king.in_check)

    def test_castling_without_checks_present(self):
        """King cannot castle out of, through, or into check."""
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/8/8/8/8/8/8/R3K2R w')
        chessboard.squares[0].name = 'Ra'
        chessboard.squares[7].name = 'Rh'
        chessboard.squares[56].name = 'ra'
        chessboard.squares[63].name = 'rh'

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertEqual(set(chessboard.white_king.moves),
                         set([2, 3, 5, 6, 11, 12, 13]))
        self.assertEqual(set(chessboard.black_king.moves),
                         set([58, 59, 61, 62, 51, 52, 53]))

    def test_castling_cannot_castle_out_of_check(self):
        """Confirm that a king cannot castle to escape check."""
        chessboard = chess_utilities.import_fen_to_board(
            '4r3/8/8/8/8/8/8/R3K2R w')
        black_rook = chessboard.squares[60]
        chessboard.squares[0].name = 'Ra'
        chessboard.squares[7].name = 'Rh'

        for piece in chessboard.white_pieces + chessboard.black_pieces:
            piece.update_moves(chessboard)

        # King has not yet realized he is in check. If these tests fail
        # because of implementation changes, they can probably be removed.
        self.assertFalse(chessboard.white_king.in_check)
        self.assertEqual(set(chessboard.white_king.moves),
                         set([2, 6, 3, 5, 11, 12, 13]))

        supposed_black_rook_moves = [56, 57, 58, 59, 61, 62, 63] \
            + list(range(4, 53, 8))
        self.assertEqual(set(black_rook.moves),
                         set(supposed_black_rook_moves))

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(set(chessboard.white_king.moves), set([3, 5, 11, 13]))

    def test_castling_cannot_castle_through_check(self):
        """Confirm a king cannot castle through an attacked square."""
        chessboard = chess_utilities.import_fen_to_board(
            '3r1r2/8/8/8/8/8/8/R3K2R w')

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertTrue(3 in chessboard.black_controlled_squares)
        self.assertTrue(5 in chessboard.black_controlled_squares)

        chessboard.white_king.update_moves(chessboard)
        self.assertEqual(chessboard.white_king.moves, [12])

    def test_castling_cannot_castle_into_check(self):
        """Confirm that the king cannot castle into an attacked square."""
        chessboard = chess_utilities.import_fen_to_board(
            '2r3r1/8/8/8/8/8/8/R3K2R w')

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertTrue(2 in chessboard.black_controlled_squares)
        self.assertTrue(6 in chessboard.black_controlled_squares)

        chessboard.white_king.update_moves(chessboard)
        self.assertEqual(set(chessboard.white_king.moves),
                         set([3, 5, 11, 12, 13]))

    def test_checked_king_moves_must_all_escape_check(self):
        """Ensure that a checked king on e1 cannot move to f1 when an
        opponent's rook is checking the king from a1.

        This functionality requires the full Board class, not the limited
        Board class previously used in the test section of pieces.py.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/8/r3K3 w')
        self.assertFalse(chessboard.white_king.in_check)

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(set(chessboard.white_king.moves),
                         set([11, 12, 13]))

    def test_escape_check_by_rook_captures_rook(self):
        """The white king has no legal moves, so the white rook must
        capture the black piece which is checking the white king.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/R6r/r3K3 w')
        white_rook_a = chessboard.squares[8]

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(chessboard.white_king.moves, [])
        self.assertEqual(white_rook_a.moves, [0])

    def test_escape_check_by_king_capturing_checking_piece(self):
        """The white king must capture the checking piece to escape check."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/7r/rK6 w')

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(chessboard.white_king.moves, [0])

    def test_king_must_escape_check_by_capturing_nonchecking_piece(self):
        """The white king must escape check by capturing a non-checking
        piece.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/7r/r6K w')

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(chessboard.white_king.moves, [15])

    def test_escape_check_by_interposition(self):
        """Test check scenario where only legal move is interposition.
        The white rook must block check.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/1R6/r7/r6K/r7 w')
        white_rook = chessboard.squares[25]
        black_rook_3 = chessboard.squares[16]
        chessboard.last_move_piece = black_rook_3

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(chessboard.white_king.moves, [])
        self.assertEqual(white_rook.moves, [9])

    def test_king_must_move_to_escape_double_check(self):
        """Test double check scenario. King must move to escape."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/8/rK5r w')
        black_rook_a = chessboard.squares[0]
        black_rook_h = chessboard.squares[7]
        chessboard.last_move_piece = black_rook_h

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.update_white_controlled_squares()

        self.assertTrue(chessboard.white_king.in_check)
        self.assertEqual(chessboard.black_controlled_squares,
                         set(black_rook_a.moves
                             + black_rook_h.moves
                             + [0, 7]))
        # black_rook_a temporarily has extra moves b/c white king is in
        # check. This is not a bug but it is important to remember.

        # self.assertEqual(set(black_rook_a.moves),
        #                 set([1] + list(range(8, 57, 8))))
        self.assertEqual(set(black_rook_h.moves),
                         set(list(range(1, 7)) + list(range(15, 64, 8))))
        # Test was failing b/c king thought black_rook_a was unprotected and
        # capturable. Fixed by protected pieces.
        self.assertEqual(set(chessboard.white_king.moves), set([9, 10]))

    def test_why_black_king_did_not_escape_check(self):
        """Recreate game scenario where black king did not escape check.

        Results: Game did not call the move-limiting method after finding
        that a king was in check (Board.moves_must_escape_check_or_checkmate).
        The issue is resolved.
        """
        chessboard = chess_utilities.import_fen_to_board(
            'rnbB2kr/1p1p3p/8/2pP2Q1/p3P3/P7/1PP2PPP/RN2KBNR b')
        self.assertEqual(chessboard.black_king.square, 62)
        self.assertIsInstance(chessboard.squares[38], pieces.Queen)
        self.assertEqual(chessboard.squares[38].color, 'white')
        chessboard.last_move_piece = chessboard.squares[38]

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertTrue(chessboard.black_king.in_check)

        for piece in chessboard.black_pieces:
            if isinstance(piece, pieces.King):
                self.assertEqual(set(piece.moves), set([61, 53]))
            else:
                self.assertEqual(piece.moves, [])

    def test_en_passant_a_file(self):
        """Test black can capture white in the A file."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/1p6/8/P7/8 w')
        white_pawn_a = chessboard.squares[8]
        black_pawn_b = chessboard.squares[25]
        black_pawn_b.has_moved = True

        chessboard.update_white_controlled_squares()
        white_pawn_a.move_piece(chessboard, 24)
        chessboard.last_move_piece = white_pawn_a
        chessboard.last_move_from_to = (8, 24)

        chessboard.update_black_controlled_squares()
        self.assertEqual(set(black_pawn_b.moves), set([17, 16]))

    def test_en_passant_h_file(self):
        """Test white can capture black in the H file."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/7p/8/6P1/8/8/8/8 w')
        white_pawn_g = chessboard.squares[38]
        black_pawn_h = chessboard.squares[55]
        white_pawn_g.has_moved = True

        chessboard.update_black_controlled_squares()
        black_pawn_h.move_piece(chessboard, 39)
        chessboard.last_move_piece = black_pawn_h
        chessboard.last_move_from_to = (55, 39)

        chessboard.update_white_controlled_squares()
        self.assertEqual(set(white_pawn_g.moves), set([46, 47]))

    def test_double_en_passant_middle(self):
        """Test black can capture white in the E file with either pawn."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/3p1p2/8/4P3/8 w')
        white_pawn_e = chessboard.squares[12]
        black_pawn_d = chessboard.squares[27]
        black_pawn_f = chessboard.squares[29]
        black_pawn_d.has_moved = True
        black_pawn_f.has_moved = True

        chessboard.update_white_controlled_squares()
        self.assertEqual(white_pawn_e.moves, [20, 28])
        white_pawn_e.move_piece(chessboard, 28)
        chessboard.last_move_piece = white_pawn_e
        chessboard.last_move_from_to = (12, 28)

        chessboard.update_black_controlled_squares()
        self.assertEqual(set(black_pawn_d.moves), set([19, 20]))
        self.assertEqual(set(black_pawn_f.moves), set([21, 20]))

    def test_close_kings_limit_moves(self):
        """Kings limit legal moves of nearby kings without limiting
        King.protected_squares or Board.<color>_controlled_squares.
        """
        chessboard = chess_utilities.import_fen_to_board(
            '1k6/8/1K6/8/8/8/8/8 w')
        chessboard.update_black_controlled_squares()
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()

        expected_white_controlled = set([48, 49, 50, 40, 42, 32, 33, 34])
        self.assertEqual(set(chessboard.white_controlled_squares),
                         expected_white_controlled)
        self.assertEqual(set(chessboard.white_king.moves),
                         set([40, 42, 32, 33, 34]))
        expected_black_controlled = set([56, 58, 48, 49, 50])
        self.assertEqual(set(chessboard.black_controlled_squares),
                         expected_black_controlled)
        self.assertEqual(set(chessboard.black_king.moves),
                         set([56, 58]))
