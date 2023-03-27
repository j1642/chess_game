"""Tests for engine.py, especially move tree search and node evaluation."""
import contextlib
import cProfile
import io
import unittest
from unittest import mock

import board
import chess_utilities
import engine
import pieces


pr = cProfile.Profile()
pr.disable()


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
            engine.evaluate_pawns_and_phase(
                chessboard,
                engine.piece_phase_values)[0],
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

        game_phase = engine.evaluate_pawns_and_phase(
            chessboard,
            engine.piece_phase_values)[1]
        self.assertEqual(game_phase, 0)

        for piece in chessboard.white_pieces:
            value = engine.white_pst_mg[piece.name[0]][piece.square]
            board_eval += value
        for piece in chessboard.black_pieces:
            value = engine.black_pst_mg[piece.name[0]][piece.square]
            board_eval -= value
        self.assertEqual(board_eval, 0)

        self.assertEqual(0.0, engine.evaluate_position(chessboard))

    def test_piece_squares_tables(self):
        """Square values reflect across the board's horizontal midline."""
        self.assertEqual(
            engine.white_pst_mg['K'][4],
            engine.black_pst_mg['k'][60])
        self.assertEqual(
            engine.white_pst_mg['K'][6],
            engine.black_pst_mg['k'][62])
        self.assertEqual(
            engine.white_pst_mg['K'][12],
            engine.black_pst_mg['k'][52])

    def test_pawn_evaluation(self):
        """Net pawn evaluation at starting position."""
        chessboard = board.Board()
        chessboard.initialize_pieces()
        self.assertEqual(
            0.0,
            engine.evaluate_pawns_and_phase(
                chessboard,
                engine.piece_phase_values)[0])

    def test_phase_eval(self):
        """Detect game phase 0 to 1 (beginning to end)."""
        chessboard = board.Board()
        # Empty board approximates end of game.
        self.assertEqual(
            engine.evaluate_pawns_and_phase(
                chessboard,
                engine.piece_phase_values)[1],
            1.0)
        # Full board for beginning of game.
        chessboard.initialize_pieces()
        self.assertEqual(
            engine.evaluate_pawns_and_phase(
                chessboard,
                engine.piece_phase_values)[1],
            0)

    def test_doubled_pawns_eval(self):
        """Detect and evaluate doubled pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/2P5/8/PPP5/8 w')
        # Update moves or eval will consider the pawns to be blocked.
        chessboard.update_white_controlled_squares()
        evaluation = engine.evaluate_pawns_and_phase(
            chessboard,
            engine.piece_phase_values)[0]
        self.assertEqual(evaluation, -50)

    def test_blocked_pawns_eval(self):
        """Detect and evaluate blocked pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/bb6/PPP5/8 w')
        chessboard.update_white_controlled_squares()
        evaluation = engine.evaluate_pawns_and_phase(
            chessboard,
            engine.piece_phase_values)[0]
        self.assertEqual(evaluation, -100)

    def test_isolated_pawns_eval(self):
        """Detect and evaluate isolated pawns."""
        chessboard = chess_utilities.import_fen_to_board(
            '8/8/8/8/8/8/P1P4P/8 w')
        chessboard.update_white_controlled_squares()
        evaluation = engine.evaluate_pawns_and_phase(
            chessboard,
            engine.piece_phase_values)[0]
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

    # Negamax throughput 240 to 340 knps, including pruned nodes.
    def test_negamax(self):
        """Search function finds the best move."""
        chessboard = chess_utilities.import_fen_to_board(
            'k7/8/8/8/6rR/8/8/K7 w')
        self.assertEqual(engine.negamax(chessboard, 4)[1], (31, 30))
        chessboard = chess_utilities.import_fen_to_board(
            'k7/8/8/8/6rR/8/8/K7 b')
        search = engine.negamax(chessboard, 4)
        self.assertEqual(search[1], (30, 31))

    def test_zobrist_undo(self):
        """Reverse hashes when undoing a move."""
        chessboard = board.Board()
        chessboard.initialize_pieces()
        chessboard.update_zobrist_hash()
        initial_hash = chessboard.zobrist_hash
        initial_ep_hash_to_undo = chessboard.ep_hash_to_undo

        engine.negamax(chessboard, 2)
        self.assertEqual(initial_hash, chessboard.zobrist_hash)
        self.assertEqual(initial_ep_hash_to_undo, chessboard.ep_hash_to_undo)

    def test_uci_isready(self):
        """UCI 'isready' command."""
        response = io.StringIO()
        with contextlib.redirect_stdout(response):
            engine.uci('isready', '', '', board.Board())
        self.assertEqual(response.getvalue(), 'readyok\n')

    def test_uci_d(self):
        """UCI 'd' command."""
        chessboard = board.Board()
        response = io.StringIO()
        with contextlib.redirect_stdout(response):
            engine.uci('d', '', '', chessboard)
        self.assertEqual(response.getvalue(),
                         ''.join(['\n', str(chessboard), '\n']))

    @mock.patch('engine.input', create=True)
    def test_uci_quit(self, mocked_input):
        """UCI quit mid-calculation."""
        mocked_input.side_effect = ['position startpos', 'go depth 4', 'quit']
        with self.assertRaises(SystemExit):
            engine.main()

    @mock.patch('engine.input', create=True)
    def test_uci_go_depth_stop_quit(self, mocked_input):
        """UCI calculation returns response."""
        # Side effect raises StopIteration when exhausted.
        mocked_input.side_effect = ['position startpos', 'go depth 4', 'stop',
                                    'quit']
        response = io.StringIO()
        with contextlib.redirect_stdout(response):
            with self.assertRaises(SystemExit):
                engine.main()
        self.assertTrue(response.getvalue() in ['bestmove b1c3\n',
                                                'bestmove b1a3\n'])

    # 380knps depth 4, 30k depth 3, including pruned, etc.
    @unittest.skip('Performance analysis, not a test.')
    def test_kiwipete(self, depth=3):
        """r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"""
        # nodes = {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690,
        #         6: 8031647685}
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w',
            autopromote=True)
        pr.enable()
        engine.negamax(chessboard, depth)
        pr.disable()
        pr.dump_stats('profile.pstat')
