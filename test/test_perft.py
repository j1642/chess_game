"""Debug the move generating functions by counting nodes of move tree."""

import unittest

import board
import chess_utilities
import pieces


# TODO: Refactor Perft. Split initial state variables into a separate
# function that returns a long tuple?
# TODO: Undo move function, portable b/w modules
def perft(chessboard, depth=None):
    """DFS through move tree and count the nodes."""
    chessboard.update_white_controlled_squares()
    chessboard.update_black_controlled_squares()
    chessboard.white_king.update_moves(chessboard)
    # Add various promotion pieces instead of defaulting to queen.
    for piece in chessboard.white_pieces + chessboard.black_pieces:
        if isinstance(piece, pieces.Pawn):
            for move in piece.moves:
                if any([move in pieces.ranks_files.rank_1,
                        move in pieces.ranks_files.rank_8]):
                    piece.moves.append((move, 'knight'))
                    piece.moves.append((move, 'bishop'))
                    piece.moves.append((move, 'rook'))

    if chessboard.last_move_piece.color == 'white':
        friendly_king = chessboard.black_king
        pieces_to_move = chessboard.black_pieces
    else:
        friendly_king = chessboard.white_king
        pieces_to_move = chessboard.white_pieces

    nodes = 0
    if depth == 1:
        # Slow. Could change to depth=0, check if in check. Quick try
        # resulted in old check AssertionError.
        if chessboard.last_move_piece.color == 'white':
            chessboard.remove_illegal_moves_for_pinned_pieces('black')
        else:
            chessboard.remove_illegal_moves_for_pinned_pieces('white')
        n_moves = sum([len(piece.moves) for piece in pieces_to_move])
        return n_moves

    for i, piece in enumerate(pieces_to_move):
        # Why does this fix Rh moving to Ng? Presumably after Ng move and
        # undo move, all chessboard.squares references point to the same
        # set of objects which are continually modified.
        chessboard.update_white_controlled_squares()
        chessboard.update_black_controlled_squares()
        chessboard.white_king.update_moves(chessboard)
        prev_moves = piece.moves
        switch_has_moved_to_False = False
        try:
            if piece.has_moved is False:
                switch_has_moved_to_False = True
        except AttributeError:
            pass
        for move in piece.moves:
            prev_occupant = chessboard.squares[move]
            try:
                if prev_occupant.color == 'white':
                    prev_occupant_ind = chessboard.white_pieces.index(
                        prev_occupant)
                else:
                    prev_occupant_ind = chessboard.black_pieces.index(
                        prev_occupant)
            except AttributeError:
                pass
            prev_square = piece.square
            prev_move_piece = chessboard.last_move_piece
            prev_move_from_to = chessboard.last_move_from_to
            piece.move_piece(chessboard, move)
            chessboard.update_white_controlled_squares()
            chessboard.update_black_controlled_squares()
            if friendly_king.check_if_in_check(
                    chessboard.white_controlled_squares,
                    chessboard.black_controlled_squares):
                friendly_king.in_check = False
            else:
                nodes += perft(chessboard, depth - 1)
            # Undo the move.
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
            chessboard.squares[prev_square] = piece
            piece.square = prev_square
            chessboard.last_move_piece = prev_move_piece
            chessboard.last_move_from_to = prev_move_from_to

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

    # Fails depth 2.
    def test_kiwipete(self, depth=1):
        """r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"""
        nodes = {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690,
                 6: 8031647685}
        chessboard = chess_utilities.import_fen_to_board(
            'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    # Fails depth 2.
    def test_position_3(self, depth=1):
        """Wiki position 3. Some captures, promotions, and checks."""
        nodes = {1: 14, 2: 191, 3: 2812, 4: 43238, 5: 674624}
        chessboard = chess_utilities.import_fen_to_board(
            '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    def test_promotion(self, depth=1):
        """Promotion FEN from rocechess.ch/perft.html"""
        nodes = {1: 24, 2: 496, 3: 9483, 4: 182838}
        chessboard = chess_utilities.import_fen_to_board(
            'n1n5/PPPk4/8/8/8/8/4Kppp/5N1N b')
        self.assertEqual(perft(chessboard, depth), nodes[depth])

    @unittest.skip('passes! ~10 sec')
    def test_short_castling_gives_check(self):
        """Short castling gives check."""
        chessboard = chess_utilities.import_fen_to_board(
            '5k2/8/8/8/8/8/8/4K2R w')
        self.assertEqual(perft(chessboard, 6), 661072)
