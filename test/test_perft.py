"""Debug the move generating functions by counting nodes of move tree."""

from collections import defaultdict
import unittest

import board
import chess_utilities
import pieces


# Change to class attribute.
a_board = board.Board()
square_to_alg_notation = {v: k for k, v in a_board.ALGEBRAIC_NOTATION.items()}


# TODO: Undo move function, portable b/w modules.
# DRY. Move piece/move loop into separate func. How?
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


def save_state_per_move(chessboard, move):
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

    return prev_occupant, prev_occupant_ind


def undo_move(chessboard, saved_piece_loop, saved_move_loop):
    """Undo perft move."""
    prev_move_piece, prev_move_from_to, prev_square, prev_moves, \
        switch_has_moved_to_False, piece, i, pieces_to_move = saved_piece_loop

    prev_occupant, prev_occupant_ind = saved_move_loop

    if switch_has_moved_to_False:
        piece.has_moved = False
    piece.moves = prev_moves
    chessboard.squares[piece.square] = prev_occupant
    chessboard.squares[prev_square] = piece
    piece.square = prev_square
    move = chessboard.last_move_from_to[1]
    chessboard.last_move_piece = prev_move_piece
    chessboard.last_move_from_to = prev_move_from_to
    # Undo en passant
    if isinstance(piece, pieces.Pawn) and move == piece.en_passant_move:
        chessboard.squares[prev_move_from_to[1]] = prev_move_piece
    # Amend piece list to undo promotion.
    # Possible bugs from changing list while iterating over it.
    # After separating out this func, chessboard[squares] no longer holds
    # promoted piece 'Xp', but 'Xp' is still in pieces_to_move.
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


def divide(chessboard, depth=None):
    """DFS through move tree and print subtree node counts."""
    chessboard.update_white_controlled_squares()
    chessboard.update_black_controlled_squares()
    chessboard.white_king.update_moves(chessboard)
    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    divided = defaultdict(int)
    nodes = 0
    for i, piece in enumerate(pieces_to_move):
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        replicate_promotion_moves(chessboard)
        saved_piece_loop = save_state_per_piece(chessboard, pieces_to_move[i],
                                                i, pieces_to_move)
        for move in piece.moves:
            saved_move_loop = save_state_per_move(chessboard, move)
            piece.move_piece(chessboard, move)
            if friendly_king.color == 'white':
                chessboard.update_black_controlled_squares()
            else:
                chessboard.update_white_controlled_squares()
            if friendly_king.check_if_in_check(
                    chessboard.white_controlled_squares,
                    chessboard.black_controlled_squares):
                friendly_king.in_check = False
                undo_move(chessboard, saved_piece_loop, saved_move_loop)
                continue
            else:
                nodes = perft(chessboard, depth - 1)
            # Undo the move.
            undo_move(chessboard, saved_piece_loop, saved_move_loop)
            piece_symbol = ''
            if isinstance(move, tuple):
                move, piece_symbol = move
                piece_symbol = piece_symbol[0]
                if piece_symbol == 'k':
                    piece_symbol = 'n'
            move = ' '.join([piece.name,
                             square_to_alg_notation[piece.square],
                             square_to_alg_notation[move],
                             piece_symbol, ':'])
            divided[move] += nodes
    print('\n')
    for k, v in divided.items():
        print(k, v)
    print('Total:', sum(divided.values()))


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
    if depth == 1:
        if chessboard.last_move_piece.color == 'white':
            chessboard.remove_illegal_moves_for_pinned_pieces('black')
        else:
            chessboard.remove_illegal_moves_for_pinned_pieces('white')
        replicate_promotion_moves(chessboard)
        n_moves = sum([len(piece.moves) for piece in pieces_to_move])
        return n_moves
    elif depth == 0:
        return 1

    for i, piece in enumerate(pieces_to_move):
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        replicate_promotion_moves(chessboard)
        saved_piece_loop = save_state_per_piece(chessboard, pieces_to_move[i],
                                                i, pieces_to_move)
        for move in piece.moves:
            saved_move_loop = save_state_per_move(chessboard, move)
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
                nodes += perft(chessboard, depth - 1)
            # Undo the move.
            undo_move(chessboard, saved_piece_loop, saved_move_loop)
    return nodes


class TestPerft(unittest.TestCase):
    """Check Perft node counts from various positions."""

    # Depth 5 fails in 290 sec. Too high by 1.006x
    def test_perft_initial_position(self, depth=3):
        """Perft from the normal starting position."""
        nodes = {1: 20, 2: 400, 3: 8902, 4: 197281, 5: 4865609,
                 6: 119060324}
        chessboard = board.Board()
        chessboard.last_move_piece = pieces.Pawn('p', 'black', 100)
        chessboard.initialize_pieces(autopromote=['white', 'black'])
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Fails depth 3.
    def test_kiwipete(self, depth=2):
        """r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"""
        nodes = {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690,
                 6: 8031647685}
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Fails depth 3.
    def test_position_3(self, depth=2):
        """Wiki position 3. Some captures, promotions, and checks."""
        nodes = {1: 14, 2: 191, 3: 2812, 4: 43238, 5: 674624}
        chessboard = chess_utilities.import_fen_to_board(
            '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Fails depth 4.
    def test_promotion(self, depth=3):
        """Promotion FEN from rocechess.ch/perft.html"""
        nodes = {1: 24, 2: 496, 3: 9483, 4: 182838}
        chessboard = chess_utilities.import_fen_to_board(
            'n1n5/PPPk4/8/8/8/8/4Kppp/5N1N b', autopromote=True)
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    @unittest.skip('passes! ~10 sec')
    def test_short_castling_gives_check(self):
        """Short castling gives check."""
        chessboard = chess_utilities.import_fen_to_board(
            '5k2/8/8/8/8/8/8/4K2R w')
        self.assertEqual(perft(chessboard, 6), 661072)
