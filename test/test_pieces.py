"""All tests for the pieces.py file."""

# from os import chdir, getcwd
# if getcwd().split('/')[-1] != 'chess':
#    chdir('..')
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
        pawn = pieces.Pawn('Pd', 'white', 11)
        friendly_piece = pieces.Bishop('Bc', 'white', 18)
        opponent_piece = pieces.Pawn('pe', 'black', 20)
        all_squares[11] = pawn
        all_squares[18] = friendly_piece
        all_squares[20] = opponent_piece

        pawn.update_moves(chessboard)
        self.assertFalse(pawn.has_moved)
        self.assertEqual(set(pawn.moves), set([19, 27, 20]))

    def test_black_pawn_captures(self):
        """Black pawns can capture white pieces and cannot move forward two
        squares when blocked by a friendly piece.
        """
        pawn = pieces.Pawn('pa', 'black', 48)
        friendly_piece = pieces.Knight('nb', 'black', 32)
        opponent_piece = pieces.Queen('Q', 'white', 41)
        all_squares[48] = pawn
        all_squares[32] = friendly_piece
        all_squares[41] = opponent_piece

        pawn.update_moves(chessboard)
        # Pawn can move forward by one (not two) or capture opponent queen.
        self.assertFalse(pawn.has_moved)
        self.assertEqual(set(pawn.moves), set([40, 41]))

    def test_pawn_cannot_capture_past_board_edge(self):
        """Opposing pawns in the A file and H file should not be able to
        capture each other.
        """
        pawn = pieces.Pawn('Pa', 'white', 8)
        opponent_pawn_b = pieces.Pawn('pb', 'black', 17)
        opponent_pawn_h = pieces.Pawn('ph', 'black', 15)
        opponent_pawn_b.has_moved = True
        opponent_pawn_h.has_moved = True
        all_squares[8] = pawn
        all_squares[17] = opponent_pawn_b
        all_squares[15] = opponent_pawn_h

        pawn.update_moves(chessboard)
        opponent_pawn_b.update_moves(chessboard)
        opponent_pawn_h.update_moves(chessboard)

        self.assertFalse(pawn.has_moved)
        self.assertTrue(opponent_pawn_b.has_moved)
        self.assertTrue(opponent_pawn_h.has_moved)

        self.assertEqual(set(pawn.moves), set([16, 24, 17]))
        self.assertEqual(set(opponent_pawn_b.moves), set([9, 8]))
        self.assertEqual(opponent_pawn_h.moves, [7])

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
        """Pawns which just captured a piece are promoted."""
        mocked_input.side_effect = ['bishop', 'rook']
        white_pawn = pieces.Pawn('Pa', 'white', 48)
        black_pawn = pieces.Pawn('pa', 'black', 8)
        white_piece_to_capture = pieces.Knight('Nb', 'white', 1)
        black_piece_to_capture = pieces.Knight('nb', 'black', 57)
        white_pawn.has_moved = True
        black_pawn.has_moved = True
        chessboard.white_pieces = [white_pawn, white_piece_to_capture]
        chessboard.black_pieces = [black_pawn, black_piece_to_capture]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

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
        knight = pieces.Knight('Ng', 'white', 6)
        pawn_e2 = pieces.Pawn('Pe', 'white', 12)
        all_squares[6] = knight
        all_squares[12] = pawn_e2

        knight.update_moves(chessboard)
        # pawn_e2 blocks one possible move from the knight's square.
        self.assertEqual(set(knight.moves), set([21, 23]))

    def test_knight_capture_available(self):
        """Knight must be able to capture opposing pieces."""
        knight = pieces.Knight('Ng', 'white', 6)
        opponent_piece = pieces.Pawn('ph', 'black', 23)
        all_squares[6] = knight
        all_squares[23] = opponent_piece

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
        bishop = pieces.Bishop('Bf', 'white', 7)
        friendly_piece = pieces.Rook('Ra', 'white', 35)
        all_squares[7] = bishop
        all_squares[35] = friendly_piece

        bishop.update_moves(chessboard)
        self.assertEqual(bishop.moves, [14, 21, 28])

    def test_bishop_opponent_piece_collision(self):
        """Bishop can move into but not past opposing pieces."""
        bishop = pieces.Bishop('Bf', 'white', 7)
        opponent_piece = pieces.Pawn('pe', 'black', 35)
        all_squares[7] = bishop
        all_squares[35] = opponent_piece

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
        rook = pieces.Rook('ra', 'black', 9)
        friendly_knight = pieces.Knight('nb', 'black', 57)
        friendly_pawn_a = pieces.Pawn('pa', 'black', 8)
        friendly_pawn_c = pieces.Pawn('pc', 'black', 10)
        all_squares[9] = rook
        all_squares[57] = friendly_knight
        all_squares[8] = friendly_pawn_a
        all_squares[10] = friendly_pawn_c

        rook.update_moves(chessboard)
        self.assertEqual(set(rook.moves), set([1] + list(range(17, 50, 8))))

    def test_rook_opponent_piece_collision(self):
        """Rook can move into but not past opposing pieces."""
        rook = pieces.Rook('ra', 'black', 9)
        opponent_pawn = pieces.Pawn('Pc', 'white', 10)
        opponent_knight = pieces.Knight('Nb', 'white', 1)
        opponent_rook = pieces.Rook('Ra', 'white', 8)
        all_squares[9] = rook
        all_squares[10] = opponent_pawn
        all_squares[1] = opponent_knight
        all_squares[8] = opponent_rook
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

        # This block should prevent queen edge cases on the corners/sides.
        queen = pieces.Queen('Q', 'white', 0)
        queen.update_moves(chessboard)
        self.assertEqual(set(queen.moves),
                         set(list(range(9, 64, 9))
                             + list(range(8, 57, 8))
                             + list(range(1, 8))))

    def test_queen_friendly_piece_collision(self):
        """Queen cannot move into or past friendly pieces."""
        queen = pieces.Queen('q', 'black', 56)
        friendly_knight = pieces.Knight('nb', 'black', 57)
        friendly_pawn = pieces.Pawn('pb', 'black', 49)
        all_squares[56] = queen
        all_squares[57] = friendly_knight
        all_squares[49] = friendly_pawn

        queen.update_moves(chessboard)
        self.assertEqual(set(queen.moves), set(range(0, 49, 8)))

    def test_queen_opponent_piece_collision(self):
        """Queen cannot move through opposing pieces but can move into
        their square.
        """
        queen = pieces.Queen('q', 'black', 0)
        opponent_bishop = pieces.Bishop('Bc', 'white', 2)
        opponent_pawn = pieces.Pawn('Pb', 'white', 9)
        all_squares[0] = queen
        all_squares[2] = opponent_bishop
        all_squares[9] = opponent_pawn

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
        white_king = pieces.King('K', 'white', 4)
        white_rook_a = pieces.Rook('Ra', 'white', 0)
        white_rook_h = pieces.Rook('Rh', 'white', 7)
        chessboard.white_pieces = [white_rook_a, white_rook_h, white_king]
        black_king = pieces.King('k', 'black', 60)
        black_rook_a = pieces.Rook('ra', 'black', 56)
        black_rook_h = pieces.Rook('rh', 'black', 63)
        chessboard.black_pieces = [black_rook_a, black_rook_h, black_king]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

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
        king = pieces.King('K', 'white', 12)
        friendly_pawn_e = pieces.Pawn('Pe', 'white', 28)
        friendly_pawn_d = pieces.Pawn('Pd', 'white', 11)
        friendly_queen = pieces.Queen('Q', 'white', 3)
        friendly_pawn_f = pieces.Pawn('Pf', 'white', 13)
        friendly_bishop = pieces.Bishop('Bf', 'white', 5)
        all_squares[12] = king
        all_squares[28] = friendly_pawn_e
        all_squares[11] = friendly_pawn_d
        all_squares[3] = friendly_queen
        all_squares[13] = friendly_pawn_f
        all_squares[5] = friendly_bishop

        king.update_moves(chessboard)
        self.assertEqual(set(king.moves), set([4, 19, 20, 21]))

    def test_remove_moves_to_attacked_squares(self):
        """Remove king moves into attacked squares."""
        white_king = pieces.King('K', 'white', 4)
        black_king = pieces.King('k', 'black', 20)
        black_rook_a = pieces.Rook('ra', 'black', 59)
        black_rook_h = pieces.Rook('rh', 'black', 61)
        all_pieces = (white_king, black_king, black_rook_a,
                      black_rook_h)
        for piece in all_pieces:
            chessboard.squares[piece.square] = piece
        for piece in all_pieces:
            piece.update_moves(chessboard)

        black_controlled_squares = set(black_rook_a.moves
                                       + black_rook_h.moves
                                       + black_king.moves)
        white_controlled_squares = set(white_king.moves)

        for king in (white_king, black_king):
            king.remove_moves_to_attacked_squares(white_controlled_squares,
                                                  black_controlled_squares)

        self.assertEqual(white_king.moves, [])
        self.assertEqual(set(black_king.moves), set([19, 21, 28, 27, 29]))

    def test_check_if_in_check(self):
        """King.check_if_in_check() method changes King.in_check to True."""
        king = pieces.King('K', 'white', 4)
        opponent_rook = pieces.Rook('ra', 'black', 0)
        self.assertFalse(king.in_check)
        all_squares[4] = king
        all_squares[0] = opponent_rook

        king.update_moves(chessboard)
        opponent_rook.update_moves(chessboard)

        king.remove_moves_to_attacked_squares(set(king.moves),
                                              set(opponent_rook.moves))
        king.check_if_in_check(set(king.moves), set(opponent_rook.moves))
        self.assertTrue(king.in_check)

    def test_castling_without_checks_present(self):
        """King cannot castle out of, through, or into check.
        This is a low-level test that checks the functions themselves, not
        how the functions are called in other files.
        """
        white_king = pieces.King('K', 'white', 4)
        white_rook_a = pieces.Rook('Ra', 'white', 0)
        white_rook_h = pieces.Rook('Rh', 'white', 7)
        black_king = pieces.King('k', 'black', 60)
        black_rook_a = pieces.Rook('ra', 'black', 56)
        black_rook_h = pieces.Rook('rh', 'black', 63)
        chessboard.white_pieces = [white_rook_a, white_rook_h, white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h, black_king]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            piece.update_moves(chessboard)

        self.assertEqual(set(white_king.moves),
                         set([2, 3, 5, 6, 11, 12, 13]))
        self.assertEqual(set(black_king.moves),
                         set([58, 59, 61, 62, 51, 52, 53]))

    def test_castling_cannot_castle_out_of_check(self):
        """Confirm that a king cannot castle to escape check."""
        king = pieces.King('K', 'white', 4)
        rook_a = pieces.Rook('Ra', 'white', 0)
        rook_h = pieces.Rook('Rh', 'white', 7)
        opponent_rook = pieces.Rook('ra', 'black', 60)
        chessboard.white_king = king
        chessboard.last_move_piece = opponent_rook
        chessboard.white_pieces = [rook_a, rook_h, king]
        chessboard.black_pieces = [opponent_rook]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            piece.update_moves(chessboard)

        # King has not yet realized he is in check. If these tests fail
        # because of changed functionality, they can probably be removed.
        self.assertFalse(king.in_check)
        self.assertEqual(set(king.moves), set([2, 6, 3, 5, 11, 12, 13]))

        supposed_opponent_rook_moves = [56, 57, 58, 59, 61, 62, 63] \
            + list(range(4, 53, 8))

        self.assertEqual(set(opponent_rook.moves),
                         set(supposed_opponent_rook_moves))

        chessboard.white_controlled_squares = set(king.moves)
        chessboard.black_controlled_squares = set(opponent_rook.moves)

        king.update_moves(chessboard)
        self.assertTrue(king.in_check)
        self.assertEqual(set(king.moves), set([3, 5, 11, 13]))

    def test_castling_cannot_castle_through_check(self):
        """Confirm a king cannot castle through an attacked square."""
        king = pieces.King('K', 'white', 4)
        rook_a = pieces.Rook('Ra', 'white', 0)
        rook_h = pieces.Rook('Rh', 'white', 7)
        opponent_rook_a = pieces.Rook('ra', 'black', 59)
        opponent_rook_h = pieces.Rook('rh', 'black', 61)
        chessboard.white_pieces = [rook_a, rook_h, king]
        chessboard.black_pieces = [opponent_rook_a, opponent_rook_h]

        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertTrue(3 in chessboard.black_controlled_squares)
        self.assertTrue(5 in chessboard.black_controlled_squares)

        king.update_moves(chessboard)

        self.assertEqual(king.moves, [12])

    def test_castling_cannot_castle_into_check(self):
        """Confirm that the king cannot castle into an attacked square."""
        king = pieces.King('K', 'white', 4)
        rook_a = pieces.Rook('Ra', 'white', 0)
        rook_h = pieces.Rook('Rh', 'white', 7)
        opponent_rook_a = pieces.Rook('ra', 'black', 58)
        opponent_rook_h = pieces.Rook('rh', 'black', 62)
        chessboard.white_pieces = [rook_a, rook_h, king]
        chessboard.black_pieces = [opponent_rook_a, opponent_rook_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertTrue(2 in chessboard.black_controlled_squares)
        self.assertTrue(6 in chessboard.black_controlled_squares)

        king.update_moves(chessboard)
        self.assertEqual(set(king.moves), set([3, 5, 11, 12, 13]))

    def test_checked_king_moves_must_all_escape_check(self):
        """Ensure that a checked king on e1 cannot move to f1 when an
        opponent's rook is checking the king from a1.

        This functionality requires the full Board class, not the limited
        Board class previously used in the test section of pieces.py.

        This test is similar to one in pieces.py but this has a crucial
        addition at the end.
        """
        king = pieces.King('K', 'white', 4)
        opponent_rook = pieces.Rook('ra', 'black', 0)
        self.assertFalse(king.in_check)
        chessboard.white_king = king
        chessboard.last_move_piece = opponent_rook
        chessboard.white_pieces.append(king)
        chessboard.black_pieces.append(opponent_rook)
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()

        king.update_moves(chessboard)

        self.assertTrue(king.in_check)
        self.assertEqual(set(king.moves), set([11, 12, 13]))

    def test_escape_check_by_rook_captures_rook(self):
        """The white king has no legal moves, so the white rook must
        capture the black piece which is checking the white king.
        """
        white_king = pieces.King('K', 'white', 4)
        white_rook_a = pieces.Rook('Ra', 'white', 8)
        black_rook_a = pieces.Rook('ra', 'black', 0)
        black_rook_h = pieces.Rook('rh', 'black', 15)
        chessboard.white_king = white_king
        chessboard.last_move_piece = black_rook_h
        chessboard.white_pieces = [white_rook_a, white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        white_king.update_moves(chessboard)

        self.assertTrue(white_king.in_check)
        self.assertEqual(white_king.moves, [])

        # This portion tests moves_must_escape_check_or_checkmate().
        chessboard.white_king = white_king
        chessboard.last_move_piece = black_rook_a

        checking_pieces = chessboard.find_checking_pieces()

        chessboard.moves_must_escape_check_or_checkmate(chessboard,
                                                        white_king,
                                                        checking_pieces)

        self.assertEqual(white_rook_a.moves, [0])

    def test_escape_check_by_king_capturing_checking_piece(self):
        """The white king must capture the checking piece to escape check."""
        white_king = pieces.King('K', 'white', 1)
        black_rook_a = pieces.Rook('ra', 'black', 0)
        black_rook_h = pieces.Rook('rh', 'black', 15)
        chessboard.last_move_piece = black_rook_h
        chessboard.white_king = white_king
        chessboard.white_pieces = [white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        white_king.update_moves(chessboard)

        self.assertTrue(white_king.in_check)
        self.assertEqual(white_king.moves, [0])

    def test_king_must_escape_check_by_capturing_nonchecking_piece(self):
        """The white king must escape check by capturing a non-checking
        piece.
        """
        white_king = pieces.King('K', 'white', 7)
        black_rook_a = pieces.Rook('ra', 'black', 0)
        black_rook_h = pieces.Rook('rh', 'black', 15)
        chessboard.white_king = white_king
        chessboard.last_move_piece = black_rook_h
        chessboard.white_pieces = [white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        white_king.update_moves(chessboard)

        self.assertTrue(white_king.in_check)
        self.assertEqual(white_king.moves, [15])

    def test_escape_check_by_interposition(self):
        """Test check scenario where only legal move is interposition.

        The white rook must block check.
        """
        white_king = pieces.King('K', 'white', 15)
        white_rook = pieces.Rook('Ra', 'white', 25)
        black_rook_1 = pieces.Rook('r1', 'black', 0)
        black_rook_2 = pieces.Rook('r2', 'black', 8)
        black_rook_3 = pieces.Rook('r3', 'black', 16)
        chessboard.last_move_piece = black_rook_3
        chessboard.white_king = white_king
        chessboard.white_pieces = [white_rook, white_king]
        chessboard.black_pieces = [black_rook_1, black_rook_2, black_rook_3]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        white_king.update_moves(chessboard)

        self.assertTrue(white_king.in_check)
        self.assertEqual(white_king.moves, [])

        # This portion tests moves_must_escape_check_or_checkmate().
        checking_pieces = chessboard.find_checking_pieces()
        # Test should pass because of rook interposition.
        chessboard.moves_must_escape_check_or_checkmate(chessboard,
                                                        white_king,
                                                        checking_pieces)
        self.assertEqual(white_rook.moves, [9])

    def test_king_must_move_to_escape_double_check(self):
        """Test double check scenario. King must move to escape."""
        white_king = pieces.King('K', 'white', 1)
        black_rook_a = pieces.Rook('ra', 'black', 0)
        black_rook_h = pieces.Rook('rh', 'black', 7)
        chessboard.last_move_piece = black_rook_h
        chessboard.white_king = white_king
        chessboard.white_pieces = [white_king]
        chessboard.black_pieces = [black_rook_a, black_rook_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        white_king.update_moves(chessboard)

        self.assertTrue(white_king.in_check)
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
        self.assertEqual(set(white_king.moves), set([9, 10]))

    def test_why_black_king_did_not_escape_check(self):
        """Recreate game scenario where black king did not escape check.

        Results: Game did not call the move-limiting method after finding
        that a king was in check (Board.moves_must_escape_check_or_checkmate).
        The issue is resolved.
        """
        check_test_fen = 'rnbB2kr/1p1p3p/8/2pP2Q1/p3P3/P7/1PP2PPP/RN2KBNR b'
        chessboard = chess_utilities.import_fen_to_board(check_test_fen)
        for piece in chessboard.squares:
            try:
                if piece.color == 'white':
                    if isinstance(piece, pieces.King):
                        chessboard.white_pieces.append(piece)
                    else:
                        chessboard.white_pieces.insert(0, piece)
                elif piece.color == 'black':
                    if isinstance(piece, pieces.King):
                        chessboard.black_pieces.append(piece)
                    else:
                        chessboard.black_pieces.insert(0, piece)

            except AttributeError:
                continue
        for black_piece in chessboard.black_pieces:
            if isinstance(black_piece, pieces.King):
                chessboard.black_king = black_piece
                black_king = chessboard.black_king
                break

        self.assertEqual(black_king.square, 62)
        self.assertIsInstance(chessboard.squares[38], pieces.Queen)
        self.assertEqual(chessboard.squares[38].color, 'white')
        chessboard.last_move_piece = chessboard.squares[38]

        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        # black_king.check_if_in_check(chessboard.white_controlled_squares,
        #                            chessboard.black_controlled_squares)

        self.assertTrue(black_king.in_check)

        for piece in chessboard.black_pieces:
            if isinstance(piece, pieces.King):
                self.assertEqual(set(piece.moves), set([61, 53]))
            else:
                self.assertEqual(piece.moves, [])

        # TODO: why is checking pieces == [(Q, Sq: 38, white),
        #                                  (Q, Sq: 38, white)]

    def test_en_passant_a_file(self):
        """Test black can capture white in the A file."""
        white_pawn_a = pieces.Pawn('Pa', 'white', 8)
        black_pawn_b = pieces.Pawn('pb', 'black', 25)
        black_pawn_b.has_moved = True
        chessboard.white_pieces = [white_pawn_a]
        chessboard.black_pieces = [black_pawn_b]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_white_controlled_squares()
        white_pawn_a.move_piece(chessboard, 24)
        self.assertEqual(white_pawn_a.square, 24)
        self.assertEqual(chessboard.squares[24], white_pawn_a)

        chessboard.last_move_piece = white_pawn_a
        chessboard.last_move_from_to = (8, 24)

        chessboard.update_black_controlled_squares()
        self.assertEqual(set(black_pawn_b.moves), set([17, 16]))

    def test_en_passant_h_file(self):
        """Test white can capture black in the H file."""
        white_pawn_g = pieces.Pawn('Pg', 'white', 38)
        black_pawn_h = pieces.Pawn('ph', 'black', 55)
        white_pawn_g.has_moved = True
        chessboard.white_pieces = [white_pawn_g]
        chessboard.black_pieces = [black_pawn_h]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_black_controlled_squares()
        self.assertEqual(black_pawn_h.moves, [47, 39])
        black_pawn_h.move_piece(chessboard, 39)
        chessboard.last_move_piece = black_pawn_h
        chessboard.last_move_from_to = (55, 39)

        self.assertEqual(chessboard.last_move_piece, black_pawn_h)
        self.assertEqual(chessboard.last_move_from_to, (55, 39))

        chessboard.update_white_controlled_squares()
        self.assertEqual(set(white_pawn_g.moves), set([46, 47]))

    def test_double_en_passant_middle(self):
        """Test black can capture white in the E file with either pawn."""
        white_pawn_e = pieces.Pawn('Pe', 'white', 12)
        black_pawn_d = pieces.Pawn('pd', 'black', 27)
        black_pawn_f = pieces.Pawn('pf', 'black', 29)
        black_pawn_d.has_moved = True
        black_pawn_f.has_moved = True
        chessboard.white_pieces = [white_pawn_e]
        chessboard.black_pieces = [black_pawn_d, black_pawn_f]
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

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
        b6 = chessboard.ALGEBRAIC_NOTATION['b6']
        b8 = chessboard.ALGEBRAIC_NOTATION['b8']
        chessboard.white_pieces.append(pieces.King('K', 'white', b6))
        chessboard.black_pieces.append(pieces.King('k', 'black', b8))
        for piece in chessboard.white_pieces + chessboard.black_pieces:
            chessboard.squares[piece.square] = piece

        chessboard.update_black_controlled_squares()
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()

        expected_white_controlled = set([48, 49, 50, 40, 42, 32, 33, 34])
        self.assertEqual(set(chessboard.white_controlled_squares),
                         expected_white_controlled)
        self.assertEqual(set(chessboard.squares[b6].moves),
                         set([40, 42, 32, 33, 34]))

        expected_black_controlled = set([56, 58, 48, 49, 50])
        self.assertEqual(set(chessboard.black_controlled_squares),
                         expected_black_controlled)
        self.assertEqual(set(chessboard.squares[b8].moves),
                         set([56, 58]))
