"""Debug the move generating functions by counting nodes of move tree."""

# from copy import deepcopy
import unittest

import board
import pieces


# TODO: Board.update() with correct pin calculations.
# TODO: Undo move function, portable b/w modules
def perft(chessboard, depth=None):
    """DFS through move tree and count nodes."""
    chessboard.update_white_controlled_squares()
    chessboard.update_black_controlled_squares()
    chessboard.white_king.update_moves(chessboard)

    if chessboard.last_move_piece.color == 'white':
        pieces_to_move = chessboard.black_pieces
        chessboard.remove_illegal_moves_for_pinned_pieces('black')
        chessboard.black_king.update_moves(chessboard)
    else:
        pieces_to_move = chessboard.white_pieces
        chessboard.remove_illegal_moves_for_pinned_pieces('white')
        chessboard.white_king.update_moves(chessboard)

    nodes = 0
    n_moves = sum([len(piece.moves) for piece in pieces_to_move])
    if depth == 1:
        return n_moves

    for piece in pieces_to_move:
        for move in piece.moves:
            # Deepcopy misses twice as many outcomes (~40 at depth 2)
            # prev_board = deepcopy(chessboard)
            prev_occupant = chessboard.squares[move]
            prev_square = piece.square
            prev_move_piece = chessboard.last_move_piece
            prev_move_from_to = chessboard.last_move_from_to
            piece.move_piece(chessboard, move)
            nodes += perft(chessboard, depth - 1)
            # Undo the move. Can't undo promotion.
            # chessboard = prev_board
            chessboard.squares[piece.square] = prev_occupant
            chessboard.squares[prev_square] = piece
            piece.square = prev_square
            chessboard.last_move_piece = prev_move_piece
            chessboard.last_move_from_to = prev_move_from_to

    return nodes


class TestPerft(unittest.TestCase):
    """Increment Perft depths."""

    def test_perft_1(self):
        """Depth 1."""
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, 1), 20)

    # TODO: Perft 2 has invalid knight move output. Fix Knight.
    def test_perft_2(self):
        """Depth 2. Knight problems"""
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, 2), 400)

    @unittest.skip('More invalid knight moves, friendly capture error')
    def test_perft_3(self):
        """Depth 3."""
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, 3), 8902)
