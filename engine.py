"""Algorithms for deciding computer moves, traversing the move tree, and
a CLI.
"""

from functools import reduce
import logging
import sys
import threading
import time

import board
import chess_utilities
import pieces

# logging.basicConfig(level=logging.DEBUG)


def reorder_piece_square_table(pst, color):
    """Given a piece-square table (list, a8 to h1), return a reordered
    list. The new order is a1 to h1, ..., a8 to h8.
    """
    if color == 'black':
        return pst
    elif color != 'white':
        raise ValueError('Invalid piece color')
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
piece_values = {'p': 100, 'n': 300, 'b': 300, 'r': 500, 'q': 900, 'k': 10000,
                'P': 100, 'N': 300, 'B': 300, 'R': 500, 'Q': 900, 'K': 10000}
piece_phase_values = {'p': 0, 'n': 1, 'b': 1, 'r': 2, 'q': 4,
                      'P': 0, 'N': 1, 'B': 1, 'R': 2, 'Q': 4}
# Transform early/middle-game piece-square tables.
black_pst_mg = piece_square_tables_mg
white_pst_mg = {}
for k, v in piece_square_tables_mg.items():
    white_pst_mg[k.upper()] = reorder_piece_square_table(v, 'white')
# Transform endgame tables.
black_pst_eg = piece_square_tables_eg
white_pst_eg = {}
for k, v in piece_square_tables_eg.items():
    white_pst_eg[k.upper()] = reorder_piece_square_table(v, 'white')

transposition = {}


def evaluate_pawns_and_phase(chessboard, piece_phase_values):
    """Return evaluation of doubled, blocked, and/or isolated pawns, in
    centipawns, and the current game phase.

    Evaluating pawns and calculating the game phase in the same loop is
    faster than two seperate loops/functions. n vs 2n.
    """
    white_eval = 0
    black_eval = 0
    white_pawns_per_file = [0] * 8
    black_pawns_per_file = [0] * 8
    phase = 24
    for piece in chessboard.white_pieces + chessboard.black_pieces:
        if piece.name[0] == 'p' or piece.name[0] == 'P':
            # Blocked pawns
            if piece.color == 'white':
                white_pawns_per_file[piece.square % 8] += 1
                if piece.square + 8 not in piece.moves:
                    white_eval -= 50
            else:
                black_pawns_per_file[piece.square % 8] += 1
                if piece.square - 8 not in piece.moves:
                    black_eval -= 50
        else:
            if not piece.name[0] == 'K' and not piece.name[0] == 'k':
                phase -= piece_phase_values[piece.name[0].lower()]
    phase = round(phase / 24)

    for color, pawns_per_file in enumerate([white_pawns_per_file,
                                            black_pawns_per_file]):
        pawn_eval = 0
        for i, pawn_count in enumerate(pawns_per_file):
            # Doubled pawns
            if pawn_count > 1:
                pawn_eval -= 25 * pawn_count
            # Isolated pawns
            if pawn_count > 0:
                try:
                    lower_neighbor = pawns_per_file[i - 1]
                except IndexError:
                    # A-pawn(s)
                    if pawns_per_file[i + 1] == 0:
                        pawn_eval -= 50
                try:
                    higher_neighbor = pawns_per_file[i + 1]
                except IndexError:
                    # H-pawn(s)
                    if pawns_per_file[i - 1] == 0:
                        pawn_eval -= 50
                if lower_neighbor == 0 == higher_neighbor:
                    pawn_eval -= 50
        if color == 0:
            white_eval += pawn_eval
        else:
            black_eval += pawn_eval

    return white_eval - black_eval, phase


def generate_move_tree(chessboard, pieces_to_move):
    """Make move tree generator."""
    move = None
    for i, piece in enumerate(pieces_to_move):
        try:
            if piece == pieces_to_move[-1] and move == piece.moves[-1]:
                StopIteration
        except IndexError:
            StopIteration
        if piece is chessboard.white_king:
            chessboard.update_black_controlled_squares()
            piece.update_moves(chessboard)
        elif piece is chessboard.black_king:
            chessboard.update_white_controlled_squares()
            piece.update_moves(chessboard)
        else:
            piece.update_moves(chessboard)
            if isinstance(piece, pieces.Pawn):
                replicate_promotion_moves(chessboard)
        saved_piece_loop = save_state_per_piece(chessboard, pieces_to_move[i],
                                                i, pieces_to_move)
        for move in piece.moves:
            saved_move_loop = save_state_per_move(chessboard, move, piece)
            piece.move_piece(chessboard, move)
            yield chessboard
            undo_move(chessboard, saved_piece_loop, saved_move_loop)


def evaluate_position(chessboard):
    """Return board position evaluation in centipawns."""
    # Piece values.
    white_position = sum([piece_values[piece.name[0]]
                          for piece in chessboard.white_pieces])
    black_position = sum([piece_values[piece.name[0]]
                          for piece in chessboard.black_pieces])
    # Piece mobility.
    white_position += 10 * len(chessboard.white_controlled_squares)
    black_position += 10 * len(chessboard.black_controlled_squares)

    total_evaluation, eg_percent = evaluate_pawns_and_phase(
        chessboard,
        piece_phase_values)
    # Opening/middlegame vs endgame phase taper.
    mg_percent = 1 - eg_percent

    # Apply piece-square tables with phase taper percentages.
    for piece in chessboard.white_pieces:
        midgame_piece_eval = white_pst_mg[piece.name[0]][piece.square]
        endgame_piece_eval = white_pst_eg[piece.name[0]][piece.square]
        white_position += midgame_piece_eval * mg_percent \
            + endgame_piece_eval * eg_percent

    for piece in chessboard.black_pieces:
        midgame_piece_eval = black_pst_mg[piece.name[0]][piece.square]
        endgame_piece_eval = black_pst_eg[piece.name[0]][piece.square]
        black_position += midgame_piece_eval * mg_percent \
            + endgame_piece_eval * eg_percent

    total_evaluation += white_position - black_position
    # Negation for negamax
    if chessboard.last_move_piece.color == 'white':
        total_evaluation *= -1
    return total_evaluation


# TODO: Fix iter. deep. weird best moves.
# Incorporate iterative deepening into search.
def iterative_deepening(chessboard, depth, max_time=5, **kwargs):
    """Move the best move piece to the front of its piece list for the
    next depth calculation.
    """
    start = time.time()
    for partial_depth in range(1, depth + 1):
        evaluation, best_move = negamax(chessboard, partial_depth, **kwargs)
        best_move_piece = chessboard.squares[best_move[0]]
        if best_move_piece.name[0] != 'k' and best_move_piece.name[0] != 'K':
            # Move ordering to speed up search function at deeper max
            # depth, as in negamax(depth=1) then negamax(depth=2).
            if best_move_piece.color == 'white':
                chessboard.white_pieces.remove(best_move_piece)
                chessboard.white_pieces.insert(0, best_move_piece)
            else:
                chessboard.black_pieces.remove(best_move_piece)
                chessboard.black_pieces.insert(0, best_move_piece)
        if max_time < (time.time() - start):
            break
    return evaluation, best_move


def negamax(chessboard, depth, alpha=float('-inf'), beta=float('inf'),
            stop=None, quit=None, searchmoves=None):
    """DFS through move tree and evaluate leaves.

    Parameters
    ----------
    chessboard : board.Board
    depth : int
        Maximum number of plies to search.
    alpha : float
    beta : float
    stop : threading.Event
        If set, stop the search.
    quit : threading.Event
        If set, quit the engine.
    searchmoves : None or list of tuples [(piece_0, move), ...]
        Group of same-colored pieces to exclusively include in the move
        tree. For uci() "go" command.

    """
    if depth == 0:
        return evaluate_position(chessboard), chessboard.last_move_from_to

    if searchmoves is None:
        if chessboard.last_move_piece.color == 'white':
            friendly_king = chessboard.black_king
            pieces_to_move = chessboard.black_pieces
        else:
            friendly_king = chessboard.white_king
            pieces_to_move = chessboard.white_pieces
    else:
        pieces_to_move = []
        moves_to_search = []
        for search_piece, search_move in searchmoves:
            pieces_to_move.append(search_piece)
            moves_to_search.append(search_move)
        if pieces_to_move[0].color == 'white':
            friendly_king = chessboard.white_king
        else:
            friendly_king = chessboard.black_king

    best_move = None
    for i, piece in enumerate(pieces_to_move):
        if piece is chessboard.white_king:
            chessboard.update_black_controlled_squares()
        elif piece is chessboard.black_king:
            chessboard.update_white_controlled_squares()
        piece.update_moves(chessboard)
        if searchmoves:
            for i, search_piece in enumerate(pieces_to_move):
                search_piece.moves = [moves_to_search[i]]
        if isinstance(piece, pieces.Pawn):
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
                try:
                    _, score, node = transposition[chessboard.zobrist_hash]
                    # Should PV nodes ever be overwritten as other node types?
                    if node == 'cutnode':
                        alpha = score
                        undo_move(chessboard, saved_piece_loop,
                                  saved_move_loop)
                        continue
                    elif node == 'allnode':
                        beta = score
                        undo_move(chessboard, saved_piece_loop,
                                  saved_move_loop)
                        continue
                    elif node == 'pvnode':
                        if score > beta:
                            best_move = chessboard.last_move_from_to
                            undo_move(chessboard, saved_piece_loop,
                                      saved_move_loop)
                            return beta, best_move
                        elif score > alpha:
                            alpha = score
                            best_move = chessboard.last_move_from_to
                            undo_move(chessboard, saved_piece_loop,
                                      saved_move_loop)
                        continue
                except KeyError:
                    values = negamax(chessboard, depth - 1, -1 * beta,
                                     -1 * alpha, stop, quit)
                    raw_score = values[0]
                    score = -1 * raw_score
                # Cut node/Type 2
                # Fail hard when score exceeds beta boundary.
                if score >= beta:
                    best_move = chessboard.last_move_from_to
                    undo_move(chessboard, saved_piece_loop, saved_move_loop)
                    transposition[chessboard.zobrist_hash] = \
                        (best_move, score, 'cutnode')
                    return beta, best_move
                # PV node/Type 1
                elif score > alpha:
                    alpha = score
                    best_move = chessboard.last_move_from_to
                    transposition[chessboard.zobrist_hash] = \
                        (best_move, score, 'pvnode')
                # All node/Type 3
                elif chessboard.zobrist_hash not in transposition:
                    transposition[chessboard.zobrist_hash] = \
                        (best_move, score, 'allnode')
                # Add depth and age to transposition table?
                # Cache invalidation based on insertion order.
                # Ideal hash table load is 0.6 to 0.75.
                # Dicts refuse new entries past 1 million, use a growth
                # factor of 3, and a starting size of 8.
                # 8 * 3^10 = 472392
                # Delete first 200,000 key/value pairs added to the
                # transposition table.
                if len(transposition) > 700_000:
                    # Iterator would be nice but gives RuntimeError
                    keys = list(transposition)[:200_000]
                    for key in keys:
                        del transposition[key]

            undo_move(chessboard, saved_piece_loop, saved_move_loop)
            try:
                if quit.is_set():
                    sys.exit(0)
                elif stop.is_set():
                    return alpha, best_move
            except AttributeError:
                pass
    return alpha, best_move


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

    zobrist_hash = chessboard.zobrist_hash
    en_passant_hash = chessboard.ep_hash_to_undo

    return prev_occupant, prev_occupant_ind, ep_captured_piece_ind, \
        zobrist_hash, en_passant_hash


def replicate_promotion_moves(chessboard):
    """Add specific promotion pieces to a pawn's moves. Assumes queen
    promotion is the default and is already accounted for.
    """
    if chessboard.last_move_piece.color == 'white':
        search_pieces = chessboard.black_pieces
    else:
        search_pieces = chessboard.white_pieces
    for piece in search_pieces:
        if piece.name[0].lower() == 'p':
            for move in piece.moves:
                if move in pieces.ranks_files.rank_1 \
                        or move in pieces.ranks_files.rank_8:
                    piece.moves.append((move, 'knight'))
                    piece.moves.append((move, 'bishop'))
                    piece.moves.append((move, 'rook'))


def undo_move(chessboard, saved_piece_loop, saved_move_loop):
    """Undo move while traversing the move tree."""
    prev_move_piece, prev_move_from_to, prev_square, prev_moves, \
        switch_has_moved_to_False, piece, i, pieces_to_move = saved_piece_loop

    prev_occupant, prev_occupant_ind, ep_captured_piece_ind, zobrist_hash,\
        en_passant_hash = saved_move_loop

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
    # Undo promotion piece list changes.
    # Carefully change list while iterating over it.
    try:
        if chessboard.last_move_piece.name[1] == 'p' \
                and isinstance(piece, pieces.Pawn):
            len_before_changes = len(pieces_to_move)
            pieces_to_move.remove(chessboard.last_move_piece)
            removed_piece = chessboard.last_move_piece
            assert removed_piece.color == piece.color
            logging.debug(f"Undo: removing {removed_piece} from piece list")
            pieces_to_move.insert(i, piece)
            logging.debug(f"Undo: adding {piece} to piece list")
            assert piece is not removed_piece
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
    # Undo hashing.
    chessboard.zobrist_hash = zobrist_hash
    chessboard.ep_hash_to_undo = en_passant_hash

    chessboard.last_move_piece = prev_move_piece
    chessboard.last_move_from_to = prev_move_from_to


def uci(command: str, stop: threading.Event, quit: threading.Event,
        chessboard):
    """Interact with the engine using the Universal Chess Interface
    (UCI).
    """
    # TODO: Complete UCI
    engine_name = 'Unnamed Engine 0.x'
    command = command.split()
    command = [word.strip() for word in command]
    assert '' not in command
    if command == []:
        return
    if len(command) == 1:
        if command[0] == 'uci':
            print('id name', engine_name)
            print('id author j1642')
            print('uciok')
            return
        elif command[0] == 'isready':
            print('readyok')
            return
        elif command[0] == 'ucinewgame':
            print('readyok')
            return
        elif command[0] == 'd':
            print('\n', chessboard, sep='')
            return
        elif command[0] == 'register':
            # Not planned.
            return
        elif command[0] == 'ucinewgame':
            # Not planned.
            return
        else:
            if command[0] in ['position', 'go']:
                return
            else:
                print('Unknown command.')
    if command[0] == 'position':
        if command[1] == 'fen':
            fen = None
            # fen = command[3:...]
            # TODO: utils cannot handle full FEN string
            chessboard = chess_utilities.import_fen_to_board(fen)
        elif command[1] == 'startpos':
            chessboard.initialize_pieces()
        elif any([chessboard.white_king is None,
                 chessboard.black_king is None,
                 len(chessboard.white_pieces + chessboard.black_pieces) < 2]):
            return
        if 'moves' in command:
            moves_ind = command.index('moves')
            for move in command[moves_ind + 1:]:
                move = move.lower()
                if not all([move[0].isalpha(), move[2].isalpha(),
                            move[1].isdigit(), move[3].isdigit,
                            len(move) == 4]):
                    return
                square_from = board.Board.ALGEBRAIC_NOTATION[move[:2]]
                square_to = board.Board.ALGEBRAIC_NOTATION[move[2:]]
                moving_piece = chessboard.squares[square_from]
                if moving_piece.color == chessboard.last_move_piece.color:
                    return
                if moving_piece == chessboard.white_king:
                    chessboard.update_black_controlled_squares()
                    chessboard.white_king.update_moves(chessboard)
                elif moving_piece == chessboard.black_king:
                    chessboard.update_white_controlled_squares()
                    chessboard.black_king.update_moves(chessboard)
                else:
                    moving_piece.update_moves(chessboard)
                if square_to not in moving_piece.moves:
                    return
                else:
                    moving_piece.move_piece(chessboard, square_to)

    elif command[0] == 'go':
        # TODO: info stdout, time commands.
        searchmoves = None
        if 'searchmoves' in command:
            # Only look at subtrees of given moves.
            searchmoves = []
            searchmoves_ind = command.index('searchmoves')
            for move in command[searchmoves_ind + 1:]:
                move = move.lower()
                if not all([move[0].isalpha(), move[2].isalpha(),
                            move[1].isdigit(), move[3].isdigit,
                            len(move) == 4]):
                    return
                square_from = board.Board.ALGEBRAIC_NOTATION[move[:2]]
                square_to = board.Board.ALGEBRAIC_NOTATION[move[2:]]
                moving_piece = chessboard.squares[square_from]
                if moving_piece.color == chessboard.last_move_piece.color:
                    return
                if moving_piece == chessboard.white_king:
                    chessboard.update_black_controlled_squares()
                    chessboard.white_king.update_moves(chessboard)
                elif moving_piece == chessboard.black_king:
                    chessboard.update_white_controlled_squares()
                    chessboard.black_king.update_moves(chessboard)
                else:
                    moving_piece.update_moves(chessboard)
                if square_to not in moving_piece.moves:
                    return
                searchmoves.append((moving_piece, square_to))

        depth = float('inf')
        if command[1] == 'depth':
            try:
                if command[2].isdigit():
                    # TODO: print "info depth 1 seldepth 0", ...
                    depth = int(command[2])
                else:
                    print('Unknown command')
                    return
            except IndexError:
                return

            def print_bestmove(depth, stop, quit):
                """Second thread, may be interrupted by Events."""
                bestmove = negamax(chessboard, depth,
                                   stop=stop, quit=quit,
                                   searchmoves=searchmoves)[1]
                bestmove = [board.Board.int_to_alg_notation[i]
                            for i in bestmove]
                print('bestmove', ''.join(bestmove))
                stop.clear()

            t2 = threading.Thread(target=print_bestmove,
                                  args=(depth, stop, quit))
            t2.start()
    elif len(command) > 1:
        print('Unknown command.')


def get_uci_input(stop: threading.Event, quit: threading.Event, chessboard):
    """Control threading.Events, pass on other inputs."""
    command = input().strip()
    if command == 'quit':
        quit.set()
        sys.exit(0)
    elif command == 'stop':
        stop.set()
    else:
        uci(command, stop, quit, chessboard)


def main():
    """CLI engine."""
    quit = threading.Event()
    stop = threading.Event()
    chessboard = board.Board()
    while not quit.is_set():
        get_uci_input(stop, quit, chessboard)
        time.sleep(0.2)


if __name__ == '__main__':
    print('Unnamed Engine 0.x')
    # TODO: complete UCI
    print('Incomplete UCI.')
    main()
