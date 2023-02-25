"""Debug the move generating functions by counting nodes of move tree."""

# from copy import deepcopy
import unittest

import board
import chess_utilities
import pieces


# TODO: Undo move function, portable b/w modules
def perft(chessboard, depth=None):
    """DFS through move tree and count the nodes."""
    chessboard.update_white_controlled_squares()
    chessboard.update_black_controlled_squares()
    chessboard.white_king.update_moves(chessboard)

    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    nodes = 0
    n_moves = sum([len(piece.moves) for piece in pieces_to_move])
    if depth == 1:
        return n_moves

    for i, piece in enumerate(pieces_to_move):
        # Why does this fix Rh moving to Ng? Presumably after Ng move and
        # undo move, all chessboard.squares references point to the same
        # set of objects which are continually modified.
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        prev_moves = piece.moves
        for move in piece.moves:
            # Deepcopy misses twice as many outcomes (~40 at depth 2)
            # prev_board = deepcopy(chessboard)
            try:
                if piece.has_moved is False:
                    switch_has_moved_to_False = True
            except AttributeError:
                switch_has_moved_to_False = False
            prev_occupant = chessboard.squares[move]
            prev_square = piece.square
            prev_move_piece = chessboard.last_move_piece
            prev_move_from_to = chessboard.last_move_from_to
            piece.move_piece(chessboard, move)
            if friendly_king.check_if_in_check(
                    chessboard.white_controlled_squares,
                    chessboard.black_controlled_squares):
                friendly_king.in_check = False
                continue
            nodes += perft(chessboard, depth - 1)
            # Undo the move.
            # chessboard = prev_board
            if switch_has_moved_to_False:
                piece.has_moved = False
            piece.moves = prev_moves
            # Amend piece list to undo promotion.
            # Possible bugs from changing list while iterating over it
            try:
                if chessboard.squares[piece.square].name[1] == 'p':
                    ind = pieces_to_move.index(
                        chessboard.squares[piece.square])
                    assert ind == 0
                    pieces_to_move.remove(chessboard.squares[piece.square])
                    pieces_to_move.insert(i, piece)
            except (AttributeError, IndexError):
                pass
            chessboard.squares[piece.square] = prev_occupant
            chessboard.squares[prev_square] = piece
            piece.square = prev_square
            chessboard.last_move_piece = prev_move_piece
            chessboard.last_move_from_to = prev_move_from_to

    return nodes


class TestPerft(unittest.TestCase):
    """Check Perft node counts from various positions."""

    # Substituting pin checks for checking if king is in check gives
    # 42,446/197,281. No errors. Need 'divide' algorithm.
    def test_perft_initial_position(self, depth=3):
        """Perft from the normal starting position."""
        nodes = {1: 20, 2: 400, 3: 8902, 4: 197281, 5: 4865609,
                 6: 119060324}
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # @unittest.skip('Failing. WIP.')
    def test_kiwipete(self, depth=1):
        """r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"""
        nodes = {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690,
                 6: 8031647685}
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w')
        self.assertEqual(perft(chessboard, depth), nodes[depth])
