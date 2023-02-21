# Minimax with alpha/beta pruning
# Inverse relation b/w time available for position eval and move searching

from functools import reduce

import board
import pieces


def reorder_piece_square_table(pst, color):
    """Given a piece-square table (list, a8 to h1), return a reordered
    list. The new order is a1 to h1, ..., a8 to h8.
    """
    # TODO: Reorder tables for black as well. White and black pieces
    # have different goal squares
    # Flexibility for testing shorter lists.
    row_length = int(len(pst) ** 0.5)
    if row_length ** 2 != len(pst):
        raise ValueError('Piece-square table length must be a square.')
    reordered = [[0] * row_length for n in range(row_length)]
    row = -1
    for i, n in enumerate(pst):
        col = i % row_length
        if col == 0:
            row += 1
        reordered[row][col] = n
    for i, row in enumerate(reordered):
        reordered[i] = list(reversed(row))
    reordered = reduce(lambda x, y: x+y, reordered)
    reordered = list(reversed(reordered))
    if color == 'white':
        return reordered


piece_values = {'p': 100, 'n': 300, 'b': 300, 'r': 500, 'q': 900,
                'k': 10000}
# TODO: Add piece-square tables to eval.
# Initially, tables are ordered from white's perspective (white home ranks
# at the bottom).
piece_square_tables_mg = {'p':
        [0,   0,   0,   0,   0,   0,  0,   0,
         98, 134,  61,  95,  68, 126, 34, -11,
         -6,   7,  26,  31,  65,  56, 25, -20,
        -14,  13,   6,  21,  23,  12, 17, -23,
        -27,  -2,  -5,  12,  17,   6, 10, -25,
        -26,  -4,  -4, -10,   3,   3, 33, -12,
        -35,  -1, -20, -23, -15,  24, 38, -22,
          0,   0,   0,   0,   0,   0,  0,   0],
    'n':
        [-167, -89, -34, -49,  61, -97, -15, -107,
         -73, -41,  72,  36,  23,  62,   7,  -17,
         -47,  60,  37,  65,  84, 129,  73,   44,
          -9,  17,  19,  53,  37,  69,  18,   22,
         -13,   4,  16,  13,  28,  19,  21,   -8,
         -23,  -9,  12,  10,  19,  17,  25,  -16,
         -29, -53, -12,  -3,  -1,  18, -14,  -19,
        -105, -21, -58, -33, -17, -28, -19,  -23],
    'b':
        [-29,   4, -82, -37, -25, -42,   7,  -8,
        -26,  16, -18, -13,  30,  59,  18, -47,
        -16,  37,  43,  40,  35,  50,  37,  -2,
         -4,   5,  19,  50,  37,  37,   7,  -2,
         -6,  13,  13,  26,  34,  12,  10,   4,
          0,  15,  15,  15,  14,  27,  18,  10,
          4,  15,  16,   0,   7,  21,  33,   1,
        -33,  -3, -14, -21, -13, -12, -39, -21],
    'r':
        [32,  42,  32,  51, 63,  9,  31,  43,
         27,  32,  58,  62, 80, 67,  26,  44,
         -5,  19,  26,  36, 17, 45,  61,  16,
        -24, -11,   7,  26, 24, 35,  -8, -20,
        -36, -26, -12,  -1,  9, -7,   6, -23,
        -45, -25, -16, -17,  3,  0,  -5, -33,
        -44, -16, -20,  -9, -1, 11,  -6, -71,
        -19, -13,   1,  17, 16,  7, -37, -26],
    'q':
        [-28,   0,  29,  12,  59,  44,  43,  45,
        -24, -39,  -5,   1, -16,  57,  28,  54,
        -13, -17,   7,   8,  29,  56,  47,  57,
        -27, -27, -16, -16,  -1,  17,  -2,   1,
         -9, -26,  -9, -10,  -2,  -4,   3,  -3,
        -14,   2, -11,  -2,  -5,   2,  14,   5,
        -35,  -8,  11,   2,   8,  15,  -3,   1,
         -1, -18,  -9,  10, -15, -25, -31, -50],
    'k':
        [-65,  23,  16, -15, -56, -34,   2,  13,
         29,  -1, -20,  -7,  -8,  -4, -38, -29,
         -9,  24,   2, -16, -20,   6,  22, -22,
        -17, -20, -12, -27, -30, -25, -14, -36,
        -49,  -1, -27, -39, -46, -44, -33, -51,
        -14, -14, -22, -46, -44, -30, -15, -27,
          1,   7,  -8, -64, -43, -16,   9,   8,
        -15,  36,  12, -54,   8, -28,  24,  14]
    }
piece_square_tables_eg = {'p':
        [0,   0,   0,   0,   0,   0,   0,   0,
        178, 173, 158, 134, 147, 132, 165, 187,
         94, 100,  85,  67,  56,  53,  82,  84,
         32,  24,  13,   5,  -2,   4,  17,  17,
         13,   9,  -3,  -7,  -7,  -8,   3,  -1,
          4,   7,  -6,   1,   0,  -5,  -1,  -8,
         13,   8,   8,  10,  13,   0,   2,  -7,
          0,   0,   0,   0,   0,   0,   0,   0],
    'n':
        [-58, -38, -13, -28, -31, -27, -63, -99,
        -25,  -8, -25,  -2,  -9, -25, -24, -52,
        -24, -20,  10,   9,  -1,  -9, -19, -41,
        -17,   3,  22,  22,  22,  11,   8, -18,
        -18,  -6,  16,  25,  16,  17,   4, -18,
        -23,  -3,  -1,  15,  10,  -3, -20, -22,
        -42, -20, -10,  -5,  -2, -20, -23, -44,
        -29, -51, -23, -15, -22, -18, -50, -64],
    'b':
        [-14, -21, -11,  -8, -7,  -9, -17, -24,
         -8,  -4,   7, -12, -3, -13,  -4, -14,
          2,  -8,   0,  -1, -2,   6,   0,   4,
         -3,   9,  12,   9, 14,  10,   3,   2,
         -6,   3,  13,  19,  7,  10,  -3,  -9,
        -12,  -3,   8,  10, 13,   3,  -7, -15,
        -14, -18,  -7,  -1,  4,  -9, -15, -27,
        -23,  -9, -23,  -5, -9, -16,  -5, -17],
    'r':
        [13, 10, 18, 15, 12,  12,   8,   5,
        11, 13, 13, 11, -3,   3,   8,   3,
         7,  7,  7,  5,  4,  -3,  -5,  -3,
         4,  3, 13,  1,  2,   1,  -1,   2,
         3,  5,  8,  4, -5,  -6,  -8, -11,
        -4,  0, -5, -1, -7, -12,  -8, -16,
        -6, -6,  0,  2, -9,  -9, -11,  -3,
        -9,  2,  3, -1, -5, -13,   4, -20],
    'q':
        [-9,  22,  22,  27,  27,  19,  10,  20,
        -17,  20,  32,  41,  58,  25,  30,   0,
        -20,   6,   9,  49,  47,  35,  19,   9,
          3,  22,  24,  45,  57,  40,  57,  36,
        -18,  28,  19,  47,  31,  34,  39,  23,
        -16, -27,  15,   6,   9,  17,  10,   5,
        -22, -23, -30, -16, -16, -23, -36, -32,
        -33, -28, -22, -43,  -5, -32, -20, -41],
    'k':
        [-74, -35, -18, -18, -11,  15,   4, -17,
        -12,  17,  14,  17,  17,  38,  23,  11,
         10,  17,  23,  15,  20,  45,  44,  13,
         -8,  22,  24,  27,  26,  33,  26,   3,
        -18,  -4,  21,  24,  27,  23,   9, -11,
        -19,  -3,  11,  21,  23,  16,   7,  -9,
        -27, -11,   4,  13,  14,   4,  -5, -17,
        -53, -34, -21, -11, -28, -14, -24, -43]
    }


def eval_doubled_blocked_isolated_pawns(chessboard) -> float:
    white_eval = 0
    black_eval = 0
    white_pawns_per_file = [0] * 8
    black_pawns_per_file = [0] * 8
    for i, board_file in enumerate(pieces.ranks_files.files):
        for square in board_file:
            if isinstance(chessboard.squares[square], pieces.Pawn):
                # Blocked pawns
                piece = chessboard.squares[square]
                if piece.square + 8 not in piece.moves \
                        and piece.square - 8 not in piece.moves:
                    if piece.color == 'white':
                        white_eval -= 500
                    else:
                        black_eval -= 500
                if piece.color == 'white':
                    white_pawns_per_file[i] += 1
                else:
                    black_pawns_per_file[i] += 1
    for color, pawns_per_file in enumerate([white_pawns_per_file,
                black_pawns_per_file]):
        pawn_eval = 0
        for i, pawn_count in enumerate(pawns_per_file):
            # Doubled pawns
            if pawn_count > 1:
                # -0.5 for doubled, -0.75 for tripled
                pawn_eval -= 500 * pawn_count / 2
            # Isolated pawns
            if pawn_count > 0:
                try:
                    lower_neighbor = pawns_per_file[i - 1]
                except IndexError:
                    # A-pawn(s)
                    if pawns_per_file[i + 1] == 0:
                        pawn_eval -= 500 * pawn_count
                assert isinstance(lower_neighbor, int)
                try:
                    higher_neighbor = pawns_per_file[i + 1]
                except IndexError:
                    # H-pawn(s)
                    if pawns_per_file[i - 1] == 0:
                        pawn_eval -= 0.5 * pawn_count
                assert isinstance(higher_neighbor, int)
                if lower_neighbor == 0 == higher_neighbor:
                    pawn_eval -= 500 * pawn_count

        if color == 0:
            white_eval += pawn_eval
        else:
            black_eval += pawn_eval
    return white_eval - black_eval


def evaluate_position(chessboard) -> float:
    """Return board position evaluation in centipawns.
    By convention, a positive value indicates white is winning, and vice
    versa for black.
    """
    # Piece values.
    white_position = sum([piece_values[piece.name[0].lower()]
            for piece in chessboard.white_pieces])
    black_position = sum([piece_values[piece.name[0].lower()]
            for piece in chessboard.black_pieces])
    # Move advantage.
    try:
        if chessboard.last_move_piece.color == 'white':
            white_position += 100
        elif chessboard.last_move_piece.color == 'black':
            black_position += 100
    except AttributeError:
        # Last move piece not set
        pass
    # Piece mobility. Better to keep or remove potential duplicates?
    white_position += 100 * len(chessboard.white_controlled_squares)
    black_position += 100 * len(chessboard.black_controlled_squares)

    total_evaluation = white_position - black_position
    total_evaluation += eval_doubled_blocked_isolated_pawns(chessboard)
    return total_evaluation


def search():
    pass


if __name__ == '__main__':
    import unittest

    class TestEngine(unittest.TestCase):
        # TODO: Seriously test eval
        def test_reorder_piece_square_table(self):
            mini_pst = [6, 7, 8,
                        3, 4, 5,
                        0, 1, 2]
            self.assertEqual(
                reorder_piece_square_table(mini_pst, 'white'),
                list(range(9)))

        def test_evaluate_position(self):
            chessboard = board.Board()
            chessboard.initialize_pieces()
            self.assertEqual(0.0, evaluate_position(chessboard))

        def test_pawn_evaluation(self):
            chessboard = board.Board()
            chessboard.initialize_pieces()
            self.assertEqual(
                0.0,
                eval_doubled_blocked_isolated_pawns(chessboard))

unittest.main()
