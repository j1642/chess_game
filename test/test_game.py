"""All tests for game.py."""

import unittest
from unittest import mock

import game
import pieces


def setup_board_kings_in_corner(g: game.Game):
    """Set up the kings and a pawn in a corner as an incomplete template
    for stalemate and checkmate.
    """
    a8 = g.board.ALGEBRAIC_NOTATION['a8']
    a7 = g.board.ALGEBRAIC_NOTATION['a7']
    a6 = g.board.ALGEBRAIC_NOTATION['a6']
    g.board.black_pieces = [pieces.King('k', 'black', a8),
                            pieces.Pawn('pa', 'black', a7)]
    g.board.white_pieces = [pieces.King('K', 'white', a6)]
    for piece in g.board.white_pieces + g.board.black_pieces:
        g.board.squares[piece.square] = piece
    g.board.white_king = g.board.squares[a6]
    g.board.black_king = g.board.squares[a8]


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
    def test_stalemates(self, mocked_input):
        """Stalemate the computer and player iteratively."""
        for player_color in ['white', 'black']:
            with self.subTest(player_color=player_color):
                mocked_input.side_effect = [player_color]
                g = game.Game()
                setup_board_kings_in_corner(g)
                if player_color == 'white':
                    g.player_king = g.board.white_king
                else:
                    g.player_king = g.board.black_king
                b1 = g.board.ALGEBRAIC_NOTATION['b1']
                g.board.squares[b1] = pieces.Rook('Ra', 'white', b1)
                g.board.white_pieces.append(g.board.squares[b1])

                g.between_moves()
                res = g.black_turn()
                self.assertEqual('stalemate', res)

    @mock.patch('game.input', create=True)
    def test_checkmates(self, mocked_input):
        """Checkmate the computer and player iteratively."""
        for player_color in ['white', 'black']:
            with self.subTest(player_color=player_color):
                mocked_input.side_effect = [player_color]
                g = game.Game()
                setup_board_kings_in_corner(g)
                g.player_king = g.board.white_king
                if player_color == 'black':
                    g.player_king = g.board.black_king
                h8 = g.board.ALGEBRAIC_NOTATION['h8']
                g.board.squares[h8] = pieces.Rook('Ra', 'white', h8)
                g.board.white_pieces.append(g.board.squares[h8])
                g.board.last_move_piece = g.board.squares[h8]
                g.board.last_move_from_to = (7, 63)

                g.between_moves()
                res = g.black_turn()
                expected = 'player wins by checkmate'
                if player_color == 'black':
                    expected = 'computer wins by checkmate'
                self.assertEqual(expected, res)

    @mock.patch('game.input', create=True)
    def test_scholars_mate(self, mocked_input):
        # Relatively slow test/
        """Reach Scholar's Mate step by step."""
        mocked_input.side_effect = ['white', 'e2', 'e4', 'd1', 'h5', 'f1',
                                    'c4', 'h5', 'f7']
        g = game.Game()
        g.board.initialize_pieces()
        for computer_move in [('e7', 'e5'), ('b8', 'c6'), ('g8', 'f6'),
                              ('f6', 'g8')]:
            g.between_moves()
            g.board.remove_illegal_moves_for_pinned_pieces('white')
            player_res = g.player_turn()
            if player_res:
                self.assertEqual(0, 1)
            g.between_moves()
            g.board.remove_illegal_moves_for_pinned_pieces('black')
            computer_res = g.computer_turn(move=computer_move)
            g.between_moves()
            if computer_res:
                break
        self.assertEqual('player wins by checkmate', computer_res)
