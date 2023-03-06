"""Tests for engine.py, especially move tree search and node evaluation."""

import unittest

import board
import chess_utilities
import engine
import pieces


class TestEngine(unittest.TestCase):
    """Search, evaluation, and piece-square table tests."""

    def test_evaluate_position(self):
        """Net zero evaluation at the starting position."""
        chessboard = board.Board()
        chessboard.initialize_pieces()
        chessboard.last_move_piece = pieces.Pawn('placeholder',
                                                 'black', 100)
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        self.assertEqual(
            engine.eval_doubled_blocked_isolated_pawns(chessboard),
            0)

        board_eval = 0
        board_eval += sum([engine.piece_values[piece.name[0].lower()]
                           for piece in chessboard.white_pieces])
        board_eval -= sum([engine.piece_values[piece.name[0].lower()]
                           for piece in chessboard.black_pieces])
        self.assertEqual(board_eval, 0)

        board_eval += 10 * len(chessboard.white_controlled_squares)
        board_eval -= 10 * len(chessboard.black_controlled_squares)
        self.assertEqual(board_eval, 0)

        game_phase = engine.early_vs_endgame_phase(chessboard)
        self.assertEqual(game_phase, 0)

        for piece in chessboard.white_pieces:
            value = engine.white_pst_mg[piece.name[0].lower()][piece.square]
            board_eval += value
        for piece in chessboard.black_pieces:
            value = engine.black_pst_mg[piece.name[0]][piece.square]
            board_eval -= value
        self.assertEqual(board_eval, 0)

        self.assertEqual(0.0, engine.evaluate_position(chessboard))

    def test_piece_squares_tables(self):
        """Square values reflect across the board's horizontal midline."""
        self.assertEqual(
            engine.white_pst_mg['k'][4],
            engine.black_pst_mg['k'][60])
        self.assertEqual(
            engine.white_pst_mg['k'][6],
            engine.black_pst_mg['k'][62])
        self.assertEqual(
            engine.white_pst_mg['k'][12],
            engine.black_pst_mg['k'][52])

    def test_pawn_evaluation(self):
        """Net pawn evaluation at starting position."""
        chessboard = board.Board()
        chessboard.initialize_pieces()
        self.assertEqual(
            0.0,
            engine.eval_doubled_blocked_isolated_pawns(chessboard))

    def test_phase_eval(self):
        """Detect game phase out of 256 (beginning, middle, end)."""
        chessboard = board.Board()
        # Empty board approximates end of game.
        self.assertEqual(
            engine.early_vs_endgame_phase(chessboard),
            256)
        chessboard.initialize_pieces()
        self.assertEqual(
            engine.early_vs_endgame_phase(chessboard),
            0)

    def test_doubled_pawns_eval(self):
        """Detect and evaluate doubled pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/2P5/8/PPP5/8 w')
        # Update moves or eval will consider the pawns to be blocked.
        chessboard.update_white_controlled_squares()
        evaluation = engine.eval_doubled_blocked_isolated_pawns(chessboard)
        self.assertEqual(evaluation, -50)

    def test_blocked_pawns_eval(self):
        """Detect and evaluate blocked pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/bb6/PPP5/8 w')
        chessboard.update_white_controlled_squares()
        evaluation = engine.eval_doubled_blocked_isolated_pawns(chessboard)
        self.assertEqual(evaluation, -100)

    def test_isolated_pawns_eval(self):
        """Detect and evaluate isolated pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/P1P4P/8 w')
        chessboard.update_white_controlled_squares()
        evaluation = engine.eval_doubled_blocked_isolated_pawns(chessboard)
        self.assertEqual(evaluation, -150)

    def test_reorder_piece_square_table(self):
        """White piece square tables require derivation."""
        mini_pst = [6, 7, 8,
                    3, 4, 5,
                    0, 1, 2]
        self.assertEqual(
            engine.reorder_piece_square_table(mini_pst, 'white'),
            list(range(9)))
        self.assertEqual(
            engine.reorder_piece_square_table(mini_pst, 'black'),
            mini_pst)
        mini_pst = [12, 13, 14, 15,
                    8, 9, 10, 11,
                    4, 5, 6, 7,
                    0, 1, 2, 3]
        self.assertEqual(
            engine.reorder_piece_square_table(mini_pst, 'white'),
            list(range(16)))
        self.assertEqual(
            engine.reorder_piece_square_table(mini_pst, 'black'),
            mini_pst)
        # Reverse essentially reflects across the two bisecting
        # axes.
        # [0, 1, 2,     [8, 7, 6,
        #  3, 4, 5, ->   5, 4, 3,
        #  6, 7, 8]      2, 1, 0]

    def test_negamax(self):
        """Search function finds the best move."""
        chessboard = chess_utilities.import_fen_to_board(
            'k7/8/8/8/6rR/8/8/K7 w')
        self.assertEqual(engine.negamax(chessboard, 3)[1], (31, 30))
        chessboard = chess_utilities.import_fen_to_board(
            'k7/8/8/8/6rR/8/8/K7 b')
        self.assertEqual(engine.negamax(chessboard, 3)[1], (30, 31))
