"""The Board class represents the chessboard, storing piece locations, the
previous move, and methods which broadly operate on each piece color.
"""
import sys
import pieces


class Board:
    """Holds the current state of the board and provides methods for
    updating the board state.

    Methods
    -------
        __init__()
        __repr__()
        initialize_pieces()
        update_moves_white()
        update_moves_black()
        update_king_moves()
        update_white_controlled_squares()
        update_black_controlled_squares()
        find_checking_pieces()
        find_interposition_squares()
        moves_must_escape_check_or_checkmate()

    """

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
        # Convert a square as algebraic notation to Board.squares index.
        self.ALGEBRAIC_NOTATION = {
            'a1': 0, 'b1': 1, 'c1': 2, 'd1': 3, 'e1': 4, 'f1': 5, 'g1': 6,
            'h1': 7, 'a2': 8, 'b2': 9, 'c2': 10, 'd2': 11, 'e2': 12,
            'f2': 13, 'g2': 14, 'h2': 15, 'a3': 16, 'b3': 17, 'c3': 18,
            'd3': 19, 'e3': 20, 'f3': 21, 'g3': 22, 'h3': 23, 'a4': 24,
            'b4': 25, 'c4': 26, 'd4': 27, 'e4': 28, 'f4': 29, 'g4': 30,
            'h4': 31, 'a5': 32, 'b5': 33, 'c5': 34, 'd5': 35, 'e5': 36,
            'f5': 37, 'g5': 38, 'h5': 39, 'a6': 40, 'b6': 41, 'c6': 42,
            'd6': 43, 'e6': 44, 'f6': 45, 'g6': 46, 'h6': 47, 'a7': 48,
            'b7': 49, 'c7': 50, 'd7': 51, 'e7': 52, 'f7': 53, 'g7': 54,
            'h7': 55, 'a8': 56, 'b8': 57, 'c8': 58, 'd8': 59, 'e8': 60,
            'f8': 61, 'g8': 62, 'h8': 63}

    def __repr__(self):
        """Start from the eighth rank (row)."""
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
        """Put all pieces on their initial squares.
        Set attributes: self.squares, self.white_pieces, self.black_pieces,
        self.white_king, self.black_king.
        """
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
                             black_knight_g, black_rook_h, black_pawn_a,
                             black_pawn_b, black_pawn_c, black_pawn_d,
                             black_pawn_e, black_pawn_f, black_pawn_g,
                             black_pawn_h]

        for piece in self.white_pieces + self.black_pieces:
            self.squares[piece.square] = piece
        self.white_king = white_king
        self.black_king = black_king

    def update_moves_white(self):
        """Support for update_white_controlled_squares() method."""
        for piece in self.white_pieces:
            piece.update_moves(self)

    def update_moves_black(self):
        """Support for update_black_controlled_squares() method."""
        for piece in self.black_pieces:
            piece.update_moves(self)

    def update_king_moves(self):
        """King moves are dependant on the possbile moves of all opponent
        pieces, so they must be updated last.
        """
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
        """Create a set to determine if black king is in check and limit
        black king moves which would put it in check.

        Note: Avoiding an "augment only" keyword argument helps avoid
        discrepancies between controlled_squares and set of one color's moves.
        """
        white_controlled_squares = []
        self.white_moves = []

        self.update_moves_white()
        for piece in self.white_pieces:
            for move in piece.moves:
                self.white_moves.append(move)
                if isinstance(piece, pieces.Pawn):
                    if abs(piece.square - move) == 7 \
                            or abs(piece.square - move) == 9:
                        white_controlled_squares.append(move)
                else:
                    white_controlled_squares.append(move)
            for square in piece.protected_squares:
                white_controlled_squares.append(square)

        self.white_controlled_squares = set(white_controlled_squares)

    def update_black_controlled_squares(self):
        """Create set to determine if white king is in check and limit
        white king moves which would put it in check.
        """
        black_controlled_squares = []
        self.black_moves = []

        self.update_moves_black()
        for piece in self.black_pieces:
            for move in piece.moves:
                self.black_moves.append(move)
                if isinstance(piece, pieces.Pawn):
                    if abs(piece.square - move) == 7 \
                            or abs(piece.square - move) == 9:
                        black_controlled_squares.append(move)
                else:
                    black_controlled_squares.append(move)
            for square in piece.protected_squares:
                black_controlled_squares.append(square)

        self.black_controlled_squares = set(black_controlled_squares)

    def find_checking_pieces(self) -> tuple:
        """Assumes a king is in check. Return which piece(s) is/are checking
        the king.
        """
        # Only one king may be in check at any time.
        if self.last_move_piece.color == 'white':
            checked_king = self.black_king
            opponent_controlled_squares = self.white_controlled_squares
            opponent_pieces = self.white_pieces
        else:
            checked_king = self.white_king
            opponent_controlled_squares = self.black_controlled_squares
            opponent_pieces = self.black_pieces

        # TODO: remove after debugging
        # print('opponent_pieces =', opponent_pieces)
        checked_square = checked_king.square
        assert checked_square in opponent_controlled_squares

        checking_pieces = []
        # Should piece move lists be sets instead?
        # Should update_moves() notice if the opponent's king is attacked?
        # TODO: pawn attacking king not in pawn moves. Use Pawn.giving_check?
        for piece in opponent_pieces:
            if isinstance(piece, pieces.Pawn):
                if checked_square in piece.protected_squares:
                    checking_pieces.append(piece)
            else:
                if checked_square in piece.moves:
                    # piece.giving_check = True
                    checking_pieces.append(piece)

        return checking_pieces  # , checked_king

    def find_interposition_squares(self, checking_pieces: list,
                                   checked_king) -> list:
        """Assumes a king is in check. Return set of interposition squares
        which block check.

        Helper function for Board.king_escapes_check_or_checkmate().
        """
        interposition_squares = []
        # Pawns and knights cannot be blocked, and kings cannot give check.
        # brq_directions = [[+-9, +-7], ...]
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
                if checked_king.square in rank \
                        and checking_piece.square in rank:
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

    def moves_must_escape_check_or_checkmate(self, board, checked_king,
                                             checking_pieces):
        """Run when a king is in check. Limits all moves to those which
        escape check. If no moves escape check, the game ends by
        checkmate.
        """
        interpose_squares = self.find_interposition_squares(checking_pieces,
                                                            checked_king)

        # King in double check must move or is in checkmate.
        if len(checking_pieces) > 1:
            if checked_king.moves == []:
                # TODO: remove after debugging
                print(checking_pieces)
                print(f'{checked_king.color.upper()} loses by checkmate.')
                sys.exit()

        checking_pieces_squares = [piece.square for piece in checking_pieces]

        if checked_king.color == 'white':
            friendly_pieces = board.white_pieces
        else:
            friendly_pieces = board.black_pieces

        # Limit moves for pieces (excluding checked king) to interposition
        # and capturing the checking piece.
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
                    piece.moves = []
                    # list(interpose_squares & set(piece.moves))
                else:
                    raise Exception('Length of checking_pieces should be >= 1')
