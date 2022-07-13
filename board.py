'''
The Board class represents the chessboard, storing piece locations, the
previous move, and methods which broadly operate on each piece color.
'''
import pieces


class Board:
    '''Holds the current state of the board and provides methods for updating
    the board state.
    '''
    def __init__(self):
        self.squares = [' '] * 64
        self.white_pieces = []
        self.black_pieces = []
        self.white_controlled_squares = []
        self.black_controlled_squares = []
        self.white_moves = []
        self.black_moves = []
        self.white_king = None
        self.black_king = None

        self.last_move_piece = None
        self.last_move_from_to = (None, None)


    def __repr__(self):
        '''Shows the current board. Useful for feedback to user before GUI
        is implememnted. Starts from the eighth rank (row).'''

        ranks_to_print = []
        for factor in range(7, -1, -1):
            rank_x = ['|']
            for square in range(factor * 8, factor * 8 + 8):
                try:
                    rank_x.append(self.squares[square].name[0])
                except AttributeError:
                    assert self.squares[square] == ' '
                    rank_x.append(self.squares[square])
                rank_x.append('|')
            ranks_to_print.append(''.join(rank_x))

        # Looks nice w/ print( <board_object> )
        return '\n'.join(ranks_to_print)


    # Variable suffix corresponds to starting file (column) of the piece.
    def initialize_pieces(self):
        white_rook_a = pieces.Rook('Ra', 'white', 0)
        white_knight_b = pieces.Knight('Nb', 'white', 1)
        white_bishop_c = pieces.Bishop('Bc', 'white', 2)
        white_queen = pieces.Queen('Q', 'white', 3)
        white_king = pieces.King('K', 'white', 4)
        white_bishop_f = pieces.Bishop('Bf', 'white', 5)
        white_knight_g = pieces.Knight('Ng', 'white', 6)
        white_rook_h = pieces.Rook('Rh', 'white', 7)

        white_pawn_a = pieces.Pawn('Pa', 'white', 8)
        white_pawn_b = pieces.Pawn('Pb', 'white', 9)
        white_pawn_c = pieces.Pawn('Pc', 'white', 10)
        white_pawn_d = pieces.Pawn('Pd', 'white', 11)
        white_pawn_e = pieces.Pawn('Pe', 'white', 12)
        white_pawn_f = pieces.Pawn('Pf', 'white', 13)
        white_pawn_g = pieces.Pawn('Pg', 'white', 14)
        white_pawn_h = pieces.Pawn('Ph', 'white', 15)

        self.white_pieces = [white_rook_a, white_knight_b, white_bishop_c,
                                white_queen, white_king, white_bishop_f,
                                white_knight_g, white_rook_h, white_pawn_a,
                                white_pawn_b, white_pawn_c, white_pawn_d,
                                white_pawn_e, white_pawn_f, white_pawn_g,
                                white_pawn_h]

        black_rook_a = pieces.Rook('ra', 'black', 56)
        black_knight_b = pieces.Knight('nb', 'black', 57)
        black_bishop_c = pieces.Bishop('bc', 'black', 58)
        black_queen = pieces.Queen('q', 'black', 59)
        black_king = pieces.King('k', 'black', 60)
        black_bishop_f = pieces.Bishop('bf', 'black', 61)
        black_knight_g = pieces.Knight('ng', 'black', 62)
        black_rook_h = pieces.Rook('rh', 'black', 63)

        black_pawn_a = pieces.Pawn('pa', 'black', 48)
        black_pawn_b = pieces.Pawn('pb', 'black', 49)
        black_pawn_c = pieces.Pawn('pc', 'black', 50)
        black_pawn_d = pieces.Pawn('pd', 'black', 51)
        black_pawn_e = pieces.Pawn('pe', 'black', 52)
        black_pawn_f = pieces.Pawn('pf', 'black', 53)
        black_pawn_g = pieces.Pawn('pg', 'black', 54)
        black_pawn_h = pieces.Pawn('ph', 'black', 55)

        self.black_pieces = [black_rook_a, black_knight_b, black_bishop_c,
                                black_queen, black_king, black_bishop_f,
                                black_knight_g, black_rook_h,black_pawn_a,
                                black_pawn_b, black_pawn_c, black_pawn_d,
                                black_pawn_e, black_pawn_f, black_pawn_g,
                                black_pawn_h]

        for piece in self.white_pieces + self.black_pieces:
            self.squares[piece.square] = piece

        self.white_king = white_king

        self.black_king = black_king


    def update_moves_white(self):
        'Helper function for update_white_controlled_squares() method.'
        for piece in self.white_pieces:
            piece.update_moves(self)


    def update_moves_black(self):
        'Helper function for update_black_controlled_squares() method.'
        for piece in self.black_pieces:
            piece.update_moves(self)


    def update_king_moves(self):
        '''The king moves are dependant on the possbile move of all opponent
        pieces, so they must be updated last.
        '''
        for piece in self.white_pieces:
            if piece.name == 'K':
                white_king = piece
                break
        for piece in self.black_pieces:
            if piece.name == 'k':
                black_king = piece
                break

        white_king.check_if_in_check(self.white_controlled_squares,
                                     self.black_controlled_squares)
        black_king.check_if_in_check(self.white_controlled_squares,
                                     self.black_controlled_squares)

        white_king.update_moves(self)
        black_king.update_moves(self)


    def update_white_controlled_squares(self):
        '''Creates set to determine if black king is in check and limit
        black king moves which would put it in check.'''
        white_controlled_squares = []
        self.white_moves = []

        self.update_moves_white()
        for piece in self.white_pieces:
            for move in piece.moves:
                self.white_moves.append(move)
                white_controlled_squares.append(move)
            for square in piece.protected_squares:
                white_controlled_squares.append(square)

        self.white_controlled_squares = set(white_controlled_squares)


    def update_black_controlled_squares(self):
        '''Creates set to determine if white king is in check and limit
        white king moves which would put it in check.'''
        black_controlled_squares = []
        self.black_moves = []

        self.update_moves_black()
        for piece in self.black_pieces:
            for move in piece.moves:
                self.black_moves.append(move)
                black_controlled_squares.append(move)
            for square in piece.protected_squares:
                black_controlled_squares.append(square)

        self.black_controlled_squares = set(black_controlled_squares)


    def find_checking_pieces(self) -> tuple:
        '''Assumes a king is in check. Return which piece(s) is/are checking
        the king and the checked king object.

        Helper function for self.king_escapes_check_or_checkmate().
        '''
        # Only one king may be in check at any time.
        if self.last_move_piece.color == 'white':
            checked_king = self.black_king
            opponent_controlled_squares = self.white_controlled_squares
            opponent_pieces = self.white_pieces
        else:
            checked_king = self.white_king
            opponent_controlled_squares = self.black_controlled_squares
            opponent_pieces = self.black_pieces

        checked_square = checked_king.square
        assert checked_square in opponent_controlled_squares

        checking_pieces = []
        # Should piece move lists be sets instead?
        # Should update_moves() notice if the opponent's king is attacked?
        for piece in opponent_pieces:
            if checked_square in piece.moves:
                #piece.giving_check = True
                checking_pieces.append(piece)

        return checking_pieces, checked_king


    def find_interposition_squares(self, checking_pieces: list,
                                   checked_king)-> list:
        '''Assumes a king is in check. Return set of interposition squares
        which block check.

        Helper function for self.king_escapes_check_or_checkmate().
        '''
        interposition_squares = []
        # Pawns and knights cannot be blocked, and kings cannot give check.
        #brq_directions = [[+-9, +-7], ...]
        for checking_piece in checking_pieces:
            delta = checked_king.square - checking_piece.square
            # max/min of +-7 in same row
            delta_is_neg = False
            if delta < 0:
                delta_is_neg = True
            # Do not add checking piece square or king square to interposing
            # moves list.
            #
            # All interposable bishop/rook/queen move deltas should be
            # divisible by an integer from 9 to 2, inclusive.
            #
            # Moves with a delta of 1 are not interposable.
            for rank in pieces.ranks_files.ranks:
                if checked_king.square in rank and checking_piece.square in rank:
                    move_direction = 1
                    break
            else:
                for move_direction in range(9, 6, -1):
                    if delta % move_direction == 0:
                        break

            assert move_direction

            if delta_is_neg:
                # Lower king square, higher piece square.
                for square in range(checking_piece.square - move_direction,
                                    checked_king.square,
                                    -1 * move_direction):
                    interposition_squares.append(square)
            else:
                # Higher king square, lower piece square.
                for square in range(checking_piece.square + move_direction,
                                    checked_king.square,
                                    move_direction):
                    interposition_squares.append(square)

        return interposition_squares


    def moves_must_escape_check_or_checkmate(self, board):
        '''Run when a king is in check. Limits all moves to those which escape
        check. If no moves escape check, the game ends by checkmate.'''
        checking_pieces, checked_king = self.find_checking_pieces()
        interpose_squares = self.find_interposition_squares(checking_pieces,
                                                            checked_king)

        # King in double check must move or is in checkmate.
        if len(checking_pieces) > 1:
            if checked_king.moves == []:
                print(f'{checked_king.color.upper()} loses by checkmate.')
                return f'{checked_king.color.upper()} loses by checkmate.'

        checking_pieces_squares = [piece.square for piece in checking_pieces]

        if checked_king.color == 'white':
            friendly_pieces = board.white_pieces
        else:
            friendly_pieces = board.black_pieces

        # Limit moves for pieces (excluding king) to interposition, and
        # capturing the checking piece.
        all_legal_moves_in_check = set(interpose_squares
                                       + checking_pieces_squares)

        piece_types_minus_king = (pieces.Pawn, pieces.Knight, pieces.Bishop,
                                  pieces.Rook, pieces.Queen)

        for piece in friendly_pieces:
            if isinstance(piece, piece_types_minus_king):
                if len(checking_pieces) == 1:
                    legal_moves = all_legal_moves_in_check & set(piece.moves)
                    piece.moves = list(legal_moves)
                elif len(checking_pieces) > 1:
                    piece.moves = list(interpose_squares & set(piece.moves))
                else:
                    raise Exception('Length of checking_pieces should be >= 1')



if __name__ == '__main__':
    import unittest


    class TestBoard(unittest.TestCase):
        '''Test: Board methods, piece movement updates Board.squares, captures
        update Board.squares, check escape scenarios, and en passant scenarios.

        Consider moving check escaping and en passant to pieces.py tests,
        or moving tests to a separate file because there are about 1000 lines
        of tests now.
        '''
        def test_repr_and_initialize_pieces(self):
            '''Test Board.__repr__() and Board.initialize_pieces().'''
            board = Board()
            board.initialize_pieces()
            self.assertEqual(len(board.white_pieces), len(board.black_pieces))
            self.assertEqual(len(board.black_pieces), 16)

            # Finally figured out how to make nice, neat multipe line strings.
            compare_to_initial_squares_repr = '|r|n|b|q|k|b|n|r|\n'\
                                '|p|p|p|p|p|p|p|p|\n'\
                                '| | | | | | | | |\n'\
                                '| | | | | | | | |\n'\
                                '| | | | | | | | |\n'\
                                '| | | | | | | | |\n'\
                                '|P|P|P|P|P|P|P|P|\n'\
                                '|R|N|B|Q|K|B|N|R|'

            self.assertEqual(board.__repr__(), compare_to_initial_squares_repr)


        def test_update_white_controlled_squares(self):
            '''Test Board.update_white_controlled_squares, which updates and
            centralizes all white piece moves currently possible.

            Board.white_controlled_squares also includes all of the protected
            squares which white pieces are on (friendly collision).
            '''
            board = Board()
            board.initialize_pieces()
            board.update_white_controlled_squares()
            squares = list(range(1, 32))
            squares.remove(7)
            self.assertEqual(board.white_controlled_squares, set(squares))


        def test_update_black_controlled_squares(self):
            '''Test Board.update_black_controlled_squares, which updates and
            centralizes all black piece moves currently possible.

            Board.black_controlled_squares also includes all of the protected
            squares which black pieces are on (friendly collision).
            '''
            board = Board()
            board.initialize_pieces()
            board.update_black_controlled_squares()
            squares = list(range(32, 63))
            squares.remove(56)
            self.assertEqual(board.black_controlled_squares, set(squares))


        def test_board_updates_upon_piece_movement(self):
            '''Test that Board.squares updates appropriately as pieces move.'''
            board = Board()
            board.initialize_pieces()

            # Test Pawn.move_piece() updates Board object.
            test_pawn = board.squares[8]
            self.assertIsInstance(test_pawn, pieces.Pawn)
            test_pawn.update_moves(board)
            test_pawn.move_piece(board, 16)
            self.assertEqual(board.squares[8], ' ')
            self.assertIsInstance(board.squares[16], pieces.Pawn)
            self.assertEqual(board.squares[16], test_pawn)

            # Remove all white pawns from the board so all other white pieces
            # can move.
            board.squares[16] = ' '
            # board.squares[8:] = [' '] sets the 8th item to ' ' and removes
            # all items past index 8. Neat feature.
            board.squares[8:16] = [' '] * 8

            for piece in board.squares[:8]:
                piece.update_moves(board)

            # Test all piece types beside pawn, which was tested above.
            new_squares = (48, 18, 16, 0, 12, 23, 21, 1)
            for ind, piece in enumerate(board.squares[:8]):
                old_square = piece.square
                new_square = new_squares[ind]

                piece.update_moves(board)
                piece.move_piece(board, new_square)

                if board.squares[old_square] == piece:
                    raise Exception(f'Invalid move for {piece.name}')

                self.assertEqual(board.squares[old_square], ' ')
                self.assertEqual(board.squares[new_square], piece)


        def test_capture_updates_board_and_piece_lists(self):
            '''Test Board.squares, Board.white_pieces, and Board.black_pieces
            update when pieces are captured.
            '''
            board = Board()
            board.initialize_pieces()
            self.assertEqual(len(board.white_pieces), len(board.black_pieces))
            self.assertEqual(len(board.black_pieces), 16)

            # Scandinavian Defense move and capture sequence.
            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            board.squares[12].move_piece(board, 28)

            board.update_black_controlled_squares()
            board.squares[51].move_piece(board, 35)

            board.update_white_controlled_squares()
            board.squares[28].move_piece(board, 35)

            self.assertEqual(len(board.black_pieces), 15)
            for piece in board.black_pieces:
                self.assertTrue(piece.name != 'pd')

            board.update_black_controlled_squares()
            board.squares[59].move_piece(board, 35)

            self.assertEqual(len(board.white_pieces), 15)
            for piece in board.white_pieces:
                self.assertTrue(piece.name != 'Pe')

            self.assertEqual(len(board.squares), 64)


        def test_checked_king_moves_must_all_escape_check(self):
            '''Ensure that a checked king on e1 cannot move to f1 when an
            opponent's rook is checking the king from a1.

            This functionality requires the full Board class, not the limited
            Board class previously used in the test section of pieces.py.

            This test is similar to one in pieces.py but this has a crucial
            addition at the end.
            '''
            board = Board()
            king = pieces.King('K', 'white', 4)
            opponent_rook = pieces.Rook('ra', 'black', 0)
            self.assertFalse(king.in_check)

            board.white_pieces.append(king)
            board.black_pieces.append(opponent_rook)

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()

            king.update_moves(board)

            self.assertTrue(king.in_check)
            self.assertEqual(set(king.moves), set([11, 12 ,13]))


        def test_escape_check_by_rook_captures_rook(self):
            '''The white king has no legal moves, so the white rook must
            capture the black piece which is checking the white king.
            '''
            board = Board()
            white_king = pieces.King('K', 'white', 4)
            white_rook_a = pieces.Rook('Ra', 'white', 8)
            black_rook_a = pieces.Rook('ra', 'black', 0)
            black_rook_h = pieces.Rook('rh', 'black', 15)

            board.white_pieces = [white_king, white_rook_a]
            board.black_pieces = [black_rook_a, black_rook_h]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            white_king.update_moves(board)

            self.assertTrue(white_king.in_check)
            self.assertEqual(white_king.moves, [])

            # This portion tests moves_must_escape_check_or_checkmate().
            board.white_king = white_king
            board.last_move_piece = black_rook_a
            board.moves_must_escape_check_or_checkmate(board)

            self.assertEqual(white_rook_a.moves, [0])


        def test_escape_check_by_king_capturing_checking_piece(self):
            '''The white king must capture the checking piece to escape check.
            '''
            board = Board()
            white_king = pieces.King('K', 'white', 1)
            black_rook_a = pieces.Rook('ra', 'black', 0)
            black_rook_h = pieces.Rook('rh', 'black', 15)

            board.white_pieces = [white_king]
            board.black_pieces = [black_rook_a, black_rook_h]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            white_king.update_moves(board)

            self.assertTrue(white_king.in_check)
            self.assertEqual(white_king.moves, [0])


        def test_king_must_escape_check_by_capturing_nonchecking_piece(self):
            '''The white king must escape check by capturing a non-checking
            piece.
            '''
            board = Board()
            white_king = pieces.King('K', 'white', 7)
            black_rook_a = pieces.Rook('ra', 'black', 0)
            black_rook_h = pieces.Rook('rh', 'black', 15)

            board.white_pieces = [white_king]
            board.black_pieces = [black_rook_a, black_rook_h]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            white_king.update_moves(board)

            self.assertTrue(white_king.in_check)
            self.assertEqual(white_king.moves, [15])


        def test_escape_check_by_interposition(self):
            '''Test check scenario where only legal move is interposition.
            The white rook must block check.'''
            board = Board()
            white_king = pieces.King('K', 'white', 15)
            white_rook = pieces.Rook('Ra', 'white', 25)
            black_rook_1 = pieces.Rook('r1', 'black', 0)
            black_rook_2 = pieces.Rook('r2', 'black', 8)
            black_rook_3 = pieces.Rook('r3', 'black', 16)

            board.white_pieces = [white_king, white_rook]
            board.black_pieces = [black_rook_1, black_rook_2, black_rook_3]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            white_king.update_moves(board)

            self.assertTrue(white_king.in_check)
            self.assertEqual(white_king.moves, [])

            # This portion tests moves_must_escape_check_or_checkmate().
            board.white_king = white_king
            board.last_move_piece = black_rook_3

            # Test should pass because of rook interposition.
            board.moves_must_escape_check_or_checkmate(board)
            self.assertEqual(white_rook.moves, [9])


        def test_king_must_move_to_escape_double_check(self):
            '''Test double check scenario where king must move to escape.'''
            board = Board()
            white_king = pieces.King('K', 'white', 1)
            black_rook_a = pieces.Rook('ra', 'black', 0)
            black_rook_h = pieces.Rook('rh', 'black', 7)

            board.white_pieces = [white_king]
            board.black_pieces = [black_rook_a, black_rook_h]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            white_king.update_moves(board)

            self.assertTrue(white_king.in_check)
            self.assertEqual(board.black_controlled_squares,
                             set(black_rook_a.moves
                                 + black_rook_h.moves
                                 + [0, 7]))
            # black_rook_a temporarily has extra moves b/c white king is in
            # check. This is not a bug but it is important to remember.
            #self.assertEqual(set(black_rook_a.moves),
            #                 set([1] + list(range(8, 57, 8))))
            self.assertEqual(set(black_rook_h.moves),
                             set(list(range(1, 7)) + list(range(15, 64, 8))))
            # Test was failing b/c king thought black_rook_a was unprotected and
            # capturable. Fixed by protected pieces.
            self.assertEqual(set(white_king.moves), set([9, 10]))


        def test_en_passant_a_file(self):
            '''Test black can capture white in the A file.'''
            board = Board()
            white_pawn_a = pieces.Pawn('Pa', 'white', 8)
            black_pawn_b = pieces.Pawn('pb', 'black', 25)
            black_pawn_b.has_moved = True

            board.white_pieces = [white_pawn_a]
            board.black_pieces = [black_pawn_b]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            white_pawn_a.move_piece(board, 24)
            self.assertEqual(white_pawn_a.square, 24)
            self.assertEqual(board.squares[24], white_pawn_a)

            board.last_move_piece = white_pawn_a
            board.last_move_from_to = (8, 24)

            board.update_black_controlled_squares()
            self.assertEqual(set(black_pawn_b.moves), set([17, 24]))


        def test_en_passant_h_file(self):
            '''Test white can capture black in the H file.'''
            board = Board()
            white_pawn_g = pieces.Pawn('Pg', 'white', 38)
            black_pawn_h = pieces.Pawn('ph', 'black', 55)
            white_pawn_g.has_moved = True

            board.white_pieces = [white_pawn_g]
            board.black_pieces = [black_pawn_h]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_black_controlled_squares()
            self.assertEqual(black_pawn_h.moves, [47, 39])
            black_pawn_h.move_piece(board, 39)
            board.last_move_piece = black_pawn_h
            board.last_move_from_to = (55, 39)

            self.assertEqual(board.last_move_piece, black_pawn_h)
            self.assertEqual(board.last_move_from_to, (55, 39))

            board.update_white_controlled_squares()
            self.assertEqual(set(white_pawn_g.moves), set([46, 39]))


        def test_double_en_passant_middle(self):
            '''Test black can capture white in the E file with either pawn.'''
            board = Board()
            white_pawn_e = pieces.Pawn('Pe', 'white', 12)
            black_pawn_d = pieces.Pawn('pd', 'black', 27)
            black_pawn_f = pieces.Pawn('pf', 'black', 29)
            black_pawn_d.has_moved = True
            black_pawn_f.has_moved = True

            board.white_pieces = [white_pawn_e]
            board.black_pieces = [black_pawn_d, black_pawn_f]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            self.assertEqual(white_pawn_e.moves, [20, 28])
            white_pawn_e.move_piece(board, 28)
            board.last_move_piece = white_pawn_e
            board.last_move_from_to = (12, 28)

            board.update_black_controlled_squares()
            self.assertEqual(set(black_pawn_d.moves), set([19, 28]))
            self.assertEqual(set(black_pawn_f.moves), set([21, 28]))


        def test_find_interposition_squares_same_rank(self):
            board = Board()
            white_rook_a = pieces.Rook('Ra', 'white', 63)
            white_rook_h = pieces.Rook('Rh', 'white', 56)
            black_king = pieces.King('k', 'black', 58)

            interpose_sqrs = board.find_interposition_squares([white_rook_a,
                                                               white_rook_h],
                                                               black_king)

            self.assertEqual(set(interpose_sqrs), set([57, 59, 60, 61, 62]))


        def test_find_interposition_squares_same_file(self):
            board = Board()
            white_rook_a = pieces.Rook('Ra', 'white', 0)
            white_rook_h = pieces.Rook('Rh', 'white', 24)
            black_king = pieces.King('k', 'black', 16)

            interpose_sqrs = board.find_interposition_squares([white_rook_a,
                                                               white_rook_h],
                                                               black_king)
            self.assertEqual(interpose_sqrs, [8])


        def test_find_interposition_squares_diagonal(self):
            board = Board()
            white_queen = pieces.Queen('Q', 'white', 0)
            black_king = pieces.King('k', 'black', 63)

            interpose_squares = board.find_interposition_squares([white_queen],
                                                                 black_king)
            # scalar getting set to 7
            self.assertEqual(set(interpose_squares), set(range(9, 63, 9)))


        def test_find_checking_pieces(self):
            board = Board()
            white_king = pieces.King('K', 'white', 4)
            black_rook_a = pieces.Rook('ra', 'black', 0)
            black_rook_h = pieces.Rook('rh', 'black', 7)
            black_queen = pieces.Queen('q', 'black', 60)

            board.white_king = white_king
            board.last_move_piece = black_rook_a
            board.white_pieces = [white_king]
            board.black_pieces = [black_rook_a, black_rook_h, black_queen]

            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece

            board.update_white_controlled_squares()
            board.update_black_controlled_squares()

            checking_pieces, checked_king = board.find_checking_pieces()
            self.assertEqual(checking_pieces, board.black_pieces)
            self.assertEqual(checked_king, white_king)




        # TODO: How to test overall game flow? It seems to work well. There
        # are too many board possibilities to test them all.


    unittest.main()
