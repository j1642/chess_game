"""All tests for game.py."""

import unittest
from unittest import mock

import game
import pieces


class TestGame(unittest.TestCase):
    """Test: user input, computer moves, stalemates, checkmated."""

    @mock.patch('game.input', create=True)
    def test_get_player_move_from(self, mocked_input):
        """Ask the player for a square to move from."""
        mocked_input.side_effect = ['white', 'a2']
        g = game.Game()
        g.board.initialize_pieces()
        square = g.get_player_move_from()
        self.assertEqual(square, 8)

    @mock.patch('game.input', create=True)
    def test_get_player_move_to(self, mocked_input):
        """Ask the player for a square to move to."""
        mocked_input.side_effect = ['black', 'a2']
        g = game.Game()
        square = g.get_player_move_to()
        self.assertEqual(square, 8)

    @mock.patch('game.input', create=True)
    def test_is_valid_square(self, mocked_input):
        """Validate integers 0 to 63, inclusive, and algebraic notation
        strings.
        """
        mocked_input.side_effect = ['black']
        g = game.Game()
        for n in range(64):
            n = str(n)
            with self.subTest(n=n):
                self.assertTrue(g.is_valid_square(n))

        for square in g.board.ALGEBRAIC_NOTATION:
            with self.subTest(square=square):
                self.assertTrue(g.is_valid_square(square))

    @mock.patch('game.input', create=True)
    def test_specific_computer_move(self, mocked_input):
        """Make a specified computer move."""
        mocked_input.side_effect = ['white']
        g = game.Game()
        g.board.initialize_pieces()
        g.between_moves()
        g.computer_turn(move=('d7', 'd5'))
        d5_square = g.board.ALGEBRAIC_NOTATION['d5']
        self.assertTrue(g.board.squares[d5_square].color == 'black')

    @mock.patch('game.input', create=True)
    def test_random_computer_move(self, mocked_input):
        """Make a random computer move."""
        mocked_input.side_effect = ['white']
        g = game.Game()
        g.board.initialize_pieces()
        g.between_moves()
        g.computer_turn()

        count_black_pieces_in_ranks_5_6 = 0
        for square in range(32, 48):
            try:
                if g.board.squares[square].color == 'black':
                    count_black_pieces_in_ranks_5_6 += 1
            except AttributeError:
                continue
        self.assertEqual(1, count_black_pieces_in_ranks_5_6)

    @mock.patch('game.input', create=True)
    def test_computer_stalemated(self, mocked_input):
        """Stalematei the computer. Black king in the corner."""
        mocked_input.side_effect = ['white']
        g = game.Game()
        a8 = g.board.ALGEBRAIC_NOTATION['a8']
        a7 = g.board.ALGEBRAIC_NOTATION['a7']
        a6 = g.board.ALGEBRAIC_NOTATION['a6']
        b1 = g.board.ALGEBRAIC_NOTATION['b1']
        g.board.squares[a8] = pieces.King('k', 'black', a8)
        g.board.squares[a7] = pieces.Pawn('pa', 'black', a7)
        g.board.squares[a6] = pieces.King('K', 'white', a6)
        g.board.squares[b1] = pieces.Rook('Ra', 'white', b1)
        g.board.black_pieces = [g.board.squares[a8], g.board.squares[a7]]
        g.board.white_pieces = [g.board.squares[a6], g.board.squares[b1]]
        g.board.white_king = g.board.squares[a6]
        g.board.black_king = g.board.squares[a8]
        g.board.last_move_piece = g.board.squares[b1]
        g.board.last_move_from_to = (2, 1)
        g.board.update_white_controlled_squares()
        g.board.update_black_controlled_squares()
        g.board.white_king.update_moves(g.board)
        g.between_moves()
        g.computer_turn()
        # TODO: React to stalemate in game.py to nicely end the game.

    def tesst_computer_checkmated(self):
        """Checkmate the computer."""
        pass

    def test_player_stalemated(self):
        """Stalemate the player."""
        pass

    def test_player_checkmated(self):
        """Checkmate the player."""
        pass

    def test_scholars_mate(self):
        """Achieve Scholar's Mate step by step."""
        pass
