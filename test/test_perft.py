"""Debug the move generating functions by counting nodes of move tree."""

import cProfile
from collections import defaultdict
import unittest

import board
import chess_utilities
from engine import replicate_promotion_moves, generate_move_tree
import pieces


pr = cProfile.Profile()
pr.disable()

# Change to class attribute.
a_board = board.Board()
square_to_alg_notation = {v: k for k, v in a_board.ALGEBRAIC_NOTATION.items()}


def divide(chessboard, depth):
    """DFS through move tree and print subtree node counts."""
    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    divided = defaultdict(int)
    nodes = 0
    for chessboard in generate_move_tree(chessboard, pieces_to_move):
        if friendly_king.color == 'white':
            chessboard.update_black_controlled_squares()
        else:
            chessboard.update_white_controlled_squares()
        if friendly_king.check_if_in_check(
                chessboard.white_controlled_squares,
                chessboard.black_controlled_squares):
            friendly_king.in_check = False
            continue
        else:
            nodes = perft(chessboard, depth - 1)

        piece_symbol = ''
        try:
            # Last move was a pawn promotion.
            if chessboard.last_move_piece.name[1] == 'p':
                move = chessboard.last_move_from_to[1]
                piece_symbol = chessboard.last_move_piece.name[0].lower()
        except IndexError:
            move = chessboard.last_move_from_to[1]
        prev_square = chessboard.last_move_from_to[0]
        piece_name = chessboard.last_move_piece.name[0]
        move = ' '.join([piece_name,
                         square_to_alg_notation[prev_square],
                         square_to_alg_notation[move],
                         piece_symbol, ':'])
        divided[move] += nodes
    print('\n')
    for k, v in divided.items():
        print(k, v)
    print('Total:', sum(divided.values()))


def perft(chessboard, depth):
    """DFS through move tree and count the nodes."""
    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    nodes = 0
    if depth == 1:
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        if chessboard.last_move_piece.color == 'white':
            chessboard.remove_illegal_moves_for_pinned_pieces('black')
        else:
            chessboard.remove_illegal_moves_for_pinned_pieces('white')
        replicate_promotion_moves(chessboard)
        n_moves = sum([len(piece.moves) for piece in pieces_to_move])
        return n_moves
    # For divide(depth=1)
    elif depth == 0:
        return 1

    for chessboard in generate_move_tree(chessboard, pieces_to_move):
        if friendly_king.color == 'white':
            w_controlled_sqrs = None
            b_controlled_sqrs = chessboard.find_sliding_controlled_squares(
                'black')
        else:
            b_controlled_sqrs = None
            w_controlled_sqrs = chessboard.find_sliding_controlled_squares(
                'white')
        if friendly_king.check_if_in_check(
                w_controlled_sqrs,
                b_controlled_sqrs):
            friendly_king.in_check = False
        else:
            nodes += perft(chessboard, depth - 1)
    return nodes


class TestPerft(unittest.TestCase):
    """Check Perft node counts from various positions."""

    # Depth 5 fails. Too high by 1.006x
    def test_perft_initial_position(self, depth=3):
        """Perft from the normal starting position."""
        nodes = {1: 20, 2: 400, 3: 8902, 4: 197281, 5: 4865609,
                 6: 119060324}
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Passes depth 4.
    def test_kiwipete(self, depth=3):
        """r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"""
        nodes = {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690,
                 6: 8031647685}
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w')
        node_count = perft(chessboard, depth)
        self.assertEqual(node_count, nodes[depth])

    # Fails depth 5.
    def test_position_3(self, depth=4):
        """Wiki position 3. Some captures, promotions, and checks."""
        nodes = {1: 14, 2: 191, 3: 2812, 4: 43238, 5: 674624}
        chessboard = chess_utilities.import_fen_to_board(
            '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w')
        # Divide 5 to this position ended with matching numbers.
        #    '8/2p5/3p4/1K6/1R3p1k/8/4P1P1/8 b')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Passes depth 5.
    def test_promotion(self, depth=4):
        """Promotion FEN from rocechess.ch/perft.html"""
        nodes = {1: 24, 2: 496, 3: 9483, 4: 182838, 5: 3605103}
        chessboard = chess_utilities.import_fen_to_board(
            'n1n5/PPPk4/8/8/8/8/4Kppp/5N1N b', autopromote=True)
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    @unittest.skip('passes! ~10 sec')
    def test_short_castling_gives_check(self):
        """Short castling gives check."""
        chessboard = chess_utilities.import_fen_to_board(
            '5k2/8/8/8/8/8/8/4K2R w')
        self.assertEqual(perft(chessboard, 6), 661072)

    def test_discovered_check_makes_en_passant_illegal(self):
        """Illegal en passant due to discoverd check."""
        chessboard = chess_utilities.import_fen_to_board(
            '5b2/4p3/8/5P2/1K6/8/8/7k b')
        self.assertEqual(perft(chessboard, 4), 4584)
        chessboard.squares[52].update_moves(chessboard)
        chessboard.squares[52].move_piece(chessboard, 36)
        # 5b2/8/8/4pP2/1K6/8/8/7k w - e6 0 1
        self.assertEqual(perft(chessboard, 1), 6)
