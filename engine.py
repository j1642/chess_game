"""Algorithms for deciding computer moves."""

from functools import reduce

import board
import chess_utilities
import pieces


def reorder_piece_square_table(pst, color):
    """Given a piece-square table (list, a8 to h1), return a reordered
    list. The new order is a1 to h1, ..., a8 to h8.
    """
    # Flexibility for testing short model lists.
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
    reordered = reduce(lambda x, y: x + y, reordered)

    if color == 'black':
        return reordered
    reordered.reverse()
    return reordered


# Initially, tables are ordered from white's perspective (white home ranks
# at the bottom). Need to reorder to use.
piece_square_tables_mg = {
    'p':
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
piece_values = {'p': 100, 'n': 300, 'b': 300, 'r': 500, 'q': 900,
                'k': 10000}
# Transform early/middle-game piece-square tables.
white_pst_mg = {}
black_pst_mg = {}
for k, v in piece_square_tables_mg.items():
    white_pst_mg[k] = reorder_piece_square_table(v, 'white')
    black_pst_mg[k] = reorder_piece_square_table(v, 'black')
# Transform endgame tables.
white_pst_eg = {}
black_pst_eg = {}
for k, v in piece_square_tables_eg.items():
    white_pst_eg[k] = reorder_piece_square_table(v, 'white')
    black_pst_eg[k] = reorder_piece_square_table(v, 'black')


def eval_doubled_blocked_isolated_pawns(chessboard):
    """Return evaluation of doubled, blocked, and/or isolated pawns, in
    centipawns.
    """
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
                        white_eval -= 50
                    else:
                        black_eval -= 50
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
                pawn_eval -= 25 * pawn_count
            # Isolated pawns
            if pawn_count > 0:
                try:
                    lower_neighbor = pawns_per_file[i - 1]
                except IndexError:
                    # A-pawn(s)
                    if pawns_per_file[i + 1] == 0:
                        pawn_eval -= 50
                assert isinstance(lower_neighbor, int)
                try:
                    higher_neighbor = pawns_per_file[i + 1]
                except IndexError:
                    # H-pawn(s)
                    if pawns_per_file[i - 1] == 0:
                        pawn_eval -= 50
                assert isinstance(higher_neighbor, int)
                if lower_neighbor == 0 == higher_neighbor:
                    pawn_eval -= 50

        if color == 0:
            white_eval += pawn_eval
        else:
            black_eval += pawn_eval
    return white_eval - black_eval


def early_vs_endgame_phase(chessboard):
    """Approximate the current stage of the game, from 0 (beginning) to
    256 (end). Fewer pieces remaining increases endgame proximity.
    """
    piece_phases = {'p': 0, 'n': 1, 'b': 1, 'r': 2, 'q': 4}
    # Initially, there are 4 bishops, knights, and rooks; and 2 queens.
    initial_phase = 4 * (1 + 1 + 2) + 4 * 2
    phase = initial_phase
    for piece in chessboard.white_pieces + chessboard.black_pieces:
        if isinstance(piece, pieces.King):
            continue
        phase -= piece_phases[piece.name[0].lower()]
    phase = (phase * 256 + (initial_phase / 2)) / initial_phase
    phase = round(phase)
    return phase


def evaluate_position(chessboard):
    """Return board position evaluation in centipawns."""
    # Piece values.
    white_position = sum([piece_values[piece.name[0].lower()]
        for piece in chessboard.white_pieces])
    black_position = sum([piece_values[piece.name[0].lower()]
        for piece in chessboard.black_pieces])
    # Piece mobility.
    white_position += 10 * len(chessboard.white_controlled_squares)
    black_position += 10 * len(chessboard.black_controlled_squares)
    # Opening/middlegame vs endgame phase taper.
    phase = early_vs_endgame_phase(chessboard)
    eg_percent = phase / 256
    mg_percent = 1 - eg_percent

    orig_white_eval = white_position
    # Apply piece-square tables with phase taper percentages.
    for piece in chessboard.white_pieces:
        midgame_piece_eval = white_pst_mg[piece.name[0].lower()][piece.square]
        endgame_piece_eval = white_pst_eg[piece.name[0].lower()][piece.square]
        white_position += midgame_piece_eval * mg_percent \
            + endgame_piece_eval * eg_percent
    #print('mg_percent =', mg_percent)
    #print('eg_percent =', eg_percent)
    #print('white delta =', white_position - orig_white_eval)

    orig_black_eval = black_position
    for piece in chessboard.black_pieces:
        midgame_piece_eval = black_pst_mg[piece.name[0].lower()][piece.square]
        endgame_piece_eval = black_pst_eg[piece.name[0].lower()][piece.square]
        black_position += midgame_piece_eval * mg_percent \
            + endgame_piece_eval * eg_percent

    #print('black delta =', black_position - orig_black_eval)

    total_evaluation = white_position - black_position
    total_evaluation += eval_doubled_blocked_isolated_pawns(chessboard)
    # Negation for negamax
    if chessboard.last_move_piece.color == 'white':
        total_evaluation *= -1
    return total_evaluation


def negamax(chessboard, depth=0):
    """DFS through move tree and evaluate leaves. Perft-ish."""
    if depth == 0:
        return evaluate_position(chessboard), chessboard.last_move_from_to

    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    max_score = -1000000
    for i, piece in enumerate(pieces_to_move):
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        replicate_promotion_moves(chessboard)
        saved_piece_loop = save_state_per_piece(chessboard, pieces_to_move[i],
                                                i, pieces_to_move)
        for move in piece.moves:
            saved_move_loop = save_state_per_move(chessboard, move, piece)
            piece.move_piece(chessboard, move)
            if friendly_king.color == 'white':
                chessboard.update_black_controlled_squares()
            else:
                chessboard.update_white_controlled_squares()
            if friendly_king.check_if_in_check(
                    chessboard.white_controlled_squares,
                    chessboard.black_controlled_squares):
                friendly_king.in_check = False
            else:
                raw_score, _ = negamax(chessboard, depth - 1)
                score = -1 * raw_score
                if score > max_score:
                    max_score = score
                    best_move = chessboard.last_move_from_to
            undo_move(chessboard, saved_piece_loop, saved_move_loop)
    return max_score, best_move


def save_state_per_piece(chessboard, piece, i, pieces_to_move):
    """Store once per Perft piece loop."""
    prev_move_piece = chessboard.last_move_piece
    prev_move_from_to = chessboard.last_move_from_to
    prev_square = piece.square
    prev_moves = piece.moves
    switch_has_moved_to_False = False
    try:
        if piece.has_moved is False:
            switch_has_moved_to_False = True
    except AttributeError:
        pass
    return prev_move_piece, prev_move_from_to, prev_square, prev_moves, \
        switch_has_moved_to_False, piece, i, pieces_to_move


# DRY. Move piece/move loop into separate func. How?
def save_state_per_move(chessboard, move, piece):
    """Store once per Perft move loop."""
    if isinstance(move, tuple):
        move, _ = move
    prev_occupant = chessboard.squares[move]
    prev_occupant_ind = None
    try:
        if prev_occupant.color == 'white':
            prev_occupant_ind = chessboard.white_pieces.index(
                prev_occupant)
        else:
            prev_occupant_ind = chessboard.black_pieces.index(
                prev_occupant)
    except AttributeError:
        pass
    ep_captured_piece_ind = None
    if isinstance(piece, pieces.Pawn) and move == piece.en_passant_move:
        ep_captured_piece = chessboard.last_move_piece
        if chessboard.last_move_piece.color == 'white':
            static_pieces = chessboard.white_pieces
        else:
            static_pieces = chessboard.black_pieces
        ep_captured_piece_ind = static_pieces.index(ep_captured_piece)

    return prev_occupant, prev_occupant_ind, ep_captured_piece_ind


def replicate_promotion_moves(chessboard):
    """Add specific promotion pieces to a pawn's moves. Assumes queen
    promotion is the default and is already accounted for.
    """
    for piece in chessboard.white_pieces + chessboard.black_pieces:
        if isinstance(piece, pieces.Pawn):
            for move in piece.moves:
                if any([move in pieces.ranks_files.rank_1,
                        move in pieces.ranks_files.rank_8]):
                    piece.moves.append((move, 'knight'))
                    piece.moves.append((move, 'bishop'))
                    piece.moves.append((move, 'rook'))


def undo_move(chessboard, saved_piece_loop, saved_move_loop):
    """Undo perft move."""
    prev_move_piece, prev_move_from_to, prev_square, prev_moves, \
        switch_has_moved_to_False, piece, i, pieces_to_move = saved_piece_loop

    prev_occupant, prev_occupant_ind, ep_captured_piece_ind = saved_move_loop

    if switch_has_moved_to_False:
        piece.has_moved = False
    piece.moves = prev_moves
    chessboard.squares[piece.square] = prev_occupant
    chessboard.squares[prev_square] = piece
    piece.square = prev_square
    move = chessboard.last_move_from_to[1]
    # Undo en passant
    if ep_captured_piece_ind is not None:
        chessboard.squares[prev_move_from_to[1]] = prev_move_piece
        if prev_move_piece.color == 'white':
            chessboard.white_pieces.insert(
                ep_captured_piece_ind,
                prev_move_piece)
        else:
            chessboard.black_pieces.insert(
                ep_captured_piece_ind,
                prev_move_piece)
    # Undo castling.
    # When moing the last piece on home row separating king/rook,
    # new rook appears on its castling square.
    if isinstance(piece, pieces.King) and prev_square in [4, 60]:
        if move in [2, 6, 58, 62]:
            if move == 2:
                rook = chessboard.squares[3]
                assert isinstance(rook, pieces.Rook)
                rook.square = 0
                chessboard.squares[0], chessboard.squares[3] = rook, ' '
            elif move == 6:
                rook = chessboard.squares[5]
                assert isinstance(rook, pieces.Rook)
                rook.square = 7
                chessboard.squares[7], chessboard.squares[5] = rook, ' '
            elif move == 58:
                rook = chessboard.squares[59]
                assert isinstance(rook, pieces.Rook)
                rook.square = 56
                chessboard.squares[56], chessboard.squares[59] = rook, ' '
            elif move == 62:
                rook = chessboard.squares[61]
                assert isinstance(rook, pieces.Rook)
                rook.square = 63
                chessboard.squares[63], chessboard.squares[61] = rook, ' '
            rook.has_moved = False
            piece.has_moved = False
    chessboard.last_move_piece = prev_move_piece
    chessboard.last_move_from_to = prev_move_from_to
    # Amend piece list to undo promotion.
    # Possible bugs from changing list while iterating over it.
    try:
        if pieces_to_move[0].name[1] == 'p':
            len_before_changes = len(pieces_to_move)
            pieces_to_move.pop(0)
            pieces_to_move.insert(i, piece)
            assert len_before_changes == len(pieces_to_move)
    except IndexError:
        pass
    try:
        if prev_occupant.color == 'white':
            assert prev_occupant not in chessboard.white_pieces
            chessboard.white_pieces.insert(
                prev_occupant_ind,
                prev_occupant)
        else:
            assert prev_occupant not in chessboard.black_pieces
            chessboard.black_pieces.insert(
                prev_occupant_ind,
                prev_occupant)
    except AttributeError:
        pass



if __name__ == '__main__':
    import unittest

    class TestEngine(unittest.TestCase):
        # TODO: Seriously test eval

        @unittest.skip('Piece square tables not equal?')
        def test_evaluate_position(self):
            chessboard = board.Board()
            chessboard.initialize_pieces()
            chessboard.last_move_piece = pieces.Pawn('placeholder',
                                                     'black', 100)
            self.assertEqual(0.0, evaluate_position(chessboard))

        def test_pawn_evaluation(self):
            chessboard = board.Board()
            chessboard.initialize_pieces()
            self.assertEqual(
                0.0,
                eval_doubled_blocked_isolated_pawns(chessboard))

        def test_phase_eval(self):
            chessboard = board.Board()
            # Empty board approximates end of game.
            self.assertEqual(
                early_vs_endgame_phase(chessboard),
                256)
            chessboard.initialize_pieces()
            self.assertEqual(
                early_vs_endgame_phase(chessboard),
                0)

        def test_doubled_pawns_eval(self):
            chessboard = chess_utilities.import_fen_to_board(
                '8/8/8/8/2P5/8/PPP5/8 w')
            # Update moves or eval thinks pawns are blocked.
            chessboard.update_white_controlled_squares()
            evaluation = eval_doubled_blocked_isolated_pawns(chessboard)
            self.assertEqual(evaluation, -50)

        def test_blocked_pawns_eval(self):
            chessboard = chess_utilities.import_fen_to_board(
                '8/8/8/8/8/bb6/PPP5/8 w')
            chessboard.update_white_controlled_squares()
            evaluation = eval_doubled_blocked_isolated_pawns(chessboard)
            self.assertEqual(evaluation, -100)

        def test_isolated_pawns_eval(self):
            chessboard = chess_utilities.import_fen_to_board(
                '8/8/8/8/8/8/P1P4P/8 w')
            chessboard.update_white_controlled_squares()
            evaluation = eval_doubled_blocked_isolated_pawns(chessboard)
            self.assertEqual(evaluation, -150)

        def test_reorder_piece_square_table(self):
            mini_pst = [6, 7, 8,
                        3, 4, 5,
                        0, 1, 2]
            self.assertEqual(
                reorder_piece_square_table(mini_pst, 'white'),
                list(range(9)))
            self.assertEqual(
                reorder_piece_square_table(mini_pst, 'black'),
                list(range(8, -1, -1)))
            # Reverse essentially reflects across the two bisecting
            # axes.
            # [0, 1, 2,     [8, 7, 6,
            #  3, 4, 5, ->   5, 4, 3,
            #  6, 7, 8]      2, 1, 0]

        def test_negamax(self):
            chessboard = chess_utilities.import_fen_to_board(
                'k7/8/8/8/6rR/8/8/K7 w')
            self.assertEqual(negamax(chessboard, 3)[1], (31, 30))
            chessboard = chess_utilities.import_fen_to_board(
                'k7/8/8/8/6rR/8/8/K7 b')
            self.assertEqual(negamax(chessboard, 3)[1], (30, 31))
            negamax(chessboard, 3)


    unittest.main()
