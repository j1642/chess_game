"""The Board class represents the chessboard. It stores piece locations,
the previous move, and methods which broadly operate on each piece color.
"""
import random

import pieces


class Board:
    """Holds the current state of the board and provides methods for
    updating the board state.

    Methods
    -------
        __init__()
        __repr__()
        initialize_pieces()
        update_zobrist_hash()
        update_moves_white()
        update_moves_black()
        update_king_moves()
        update_white_controlled_squares()
        update_black_controlled_squares()
        find_checking_pieces()
        find_interposition_squares()
        moves_must_escape_check_or_checkmate()

    """

    ALGEBRAIC_NOTATION = {
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
    int_to_alg_notation = {v: k for k, v in ALGEBRAIC_NOTATION.items()}

    random.seed(104)
    hash_nums = []
    # PNBRQKpnbrqk on squares [0, 64).
    for _ in range(len('PNBRQKpnbrqk')):
        hash_nums.append([random.randint(0, 2 ** 64 - 1) for i in range(64)])
    # Black to move is True.
    hash_nums.append(random.randint(0, 2 ** 64 - 1))
    # File of a valid ep square, A to H.
    hash_nums.append([random.randint(0, 2 ** 64 - 1) for i in range(8)])
    # Castling available. K kingside, K queenside, k kingside, k queenside.
    hash_nums.append([random.randint(0, 2 ** 64 - 1) for i in range(4)])

    def __init__(self):
        self.squares = [' '] * 64
        self.white_pieces = []
        self.black_pieces = []
        self.white_controlled_squares = []
        self.black_controlled_squares = []
        self.white_king = None
        self.black_king = None
        self.last_move_piece = None
        self.last_move_from_to = (-1, -1)
        self.zobrist_hash = 0
        self.ep_hash_to_undo = None
        self.applied_initial_castling_hash = False

    def __repr__(self):
        """Print the board setup, starting from the eighth rank (row)."""
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
        return '\n'.join(ranks_to_print)

    # Variable suffix corresponds to starting file (column) of the piece.
    def initialize_pieces(self, autopromote=[]):
        """Put all pieces on their initial squares. Adding a piece color
        to 'autopromote' labels those pawns for automatic queen promotion.
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
                             white_queen, white_bishop_f,
                             white_knight_g, white_rook_h, white_pawn_a,
                             white_pawn_b, white_pawn_c, white_pawn_d,
                             white_pawn_e, white_pawn_f, white_pawn_g,
                             white_pawn_h, white_king]

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
                             black_queen, black_bishop_f,
                             black_knight_g, black_rook_h, black_pawn_a,
                             black_pawn_b, black_pawn_c, black_pawn_d,
                             black_pawn_e, black_pawn_f, black_pawn_g,
                             black_pawn_h, black_king]

        for piece in self.white_pieces + self.black_pieces:
            self.squares[piece.square] = piece
        self.white_king = white_king
        self.black_king = black_king

        if autopromote:
            for color in autopromote:
                if color not in ['white', 'black']:
                    raise ValueError('Invalid color for autopromotion.')
            autopromote_pieces = []
            if 'white' in autopromote:
                autopromote_pieces += self.white_pieces
            # Specifically not elif.
            if 'black' in autopromote:
                autopromote_pieces += self.black_pieces
            for piece in autopromote_pieces:
                if isinstance(piece, pieces.Pawn):
                    piece.autopromote = True

        self.last_move_piece = pieces.Pawn('placeholder',
                                           'black',
                                           100)
        self.last_move_from_to = (-1, -1)

    def update_zobrist_hash(self, changed_pieces=None, switch_turn=False,
                            lose_castling=False):
        """Return Zobrist hash of the position and update hash attribute."""
        if switch_turn:
            self.zobrist_hash ^= self.hash_nums[12]
        if not changed_pieces:
            changed_pieces = self.white_pieces + self.black_pieces
        for piece in changed_pieces:
            if piece.color == 'white':
                color = 0
            else:
                color = 6
            piece_name = piece.name[0].lower()
            # If/elif should be faster than for loop? Not profiled.
            if piece_name == 'p':
                piece_type = 0
            elif piece_name == 'n':
                piece_type = 1
            elif piece_name == 'b':
                piece_type = 2
            elif piece_name == 'r':
                piece_type = 3
            elif piece_name == 'q':
                piece_type = 4
            elif piece_name == 'k':
                piece_type = 5
            else:
                raise ValueError(f'Invalid name: {piece.name}')
            self.zobrist_hash ^= \
                self.hash_nums[color + piece_type][piece.square]

        if self.ep_hash_to_undo is not None:
            self.zobrist_hash ^= self.ep_hash_to_undo
            self.ep_hash_to_undo = None
        if all([self.last_move_piece.name[0].lower() == 'p',
                abs(self.last_move_from_to[0]
                    - self.last_move_from_to[1]) == 16]):
            self.zobrist_hash ^= self.hash_nums[13][piece.square % 8]
            self.ep_hash_to_undo = self.hash_nums[13][piece.square % 8]

        kings_rooks_on_start_squares = False
        if not self.applied_initial_castling_hash:
            if self.white_king is self.squares[4] \
                    and self.black_king is self.squares[60] \
                    and isinstance(self.squares[0], pieces.Rook) \
                    and isinstance(self.squares[7], pieces.Rook) \
                    and isinstance(self.squares[56], pieces.Rook) \
                    and isinstance(self.squares[63], pieces.Rook) \
                    and self.squares[0].color == 'white' \
                    and self.squares[7].color == 'white' \
                    and self.squares[56].color == 'black' \
                    and self.squares[63].color == 'black' \
                    and self.squares[0].has_moved is False \
                    and self.squares[7].has_moved is False \
                    and self.squares[56].has_moved is False \
                    and self.squares[63].has_moved is False \
                    and self.white_king.has_moved is False \
                    and self.black_king.has_moved is False:
                kings_rooks_on_start_squares = True
        if not self.applied_initial_castling_hash \
                and kings_rooks_on_start_squares:
            for hash_num in self.hash_nums[14]:
                self.zobrist_hash ^= hash_num
            self.applied_initial_castling_hash = True

        if lose_castling and self.white_king and self.black_king:
            for piece in changed_pieces:
                if piece is self.white_king:
                    self.zobrist_hash ^= self.hash_nums[14][0]
                    self.zobrist_hash ^= self.hash_nums[14][1]
                elif piece is self.black_king:
                    self.zobrist_hash ^= self.hash_nums[14][2]
                    self.zobrist_hash ^= self.hash_nums[14][3]
                elif isinstance(piece, pieces.Rook):
                    if piece.color == 'white':
                        friendly_king = self.white_king
                    else:
                        friendly_king = self.black_king
                    if not piece.has_moved and not friendly_king.has_moved:
                        if piece.square == 7:
                            self.zobrist_hash ^= self.hash_nums[14][0]
                        elif piece.square == 0:
                            self.zobrist_hash ^= self.hash_nums[14][1]
                        elif piece.square == 63:
                            self.zobrist_hash ^= self.hash_nums[14][2]
                        elif piece.square == 56:
                            self.zobrist_hash ^= self.hash_nums[14][3]
                        else:
                            raise ValueError('invalid rook square')

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

        for piece in self.white_pieces:
            piece.update_moves(self)
            if not isinstance(piece, pieces.Pawn):
                for move in piece.moves:
                    white_controlled_squares.append(move)
            for square in piece.protected_squares:
                white_controlled_squares.append(square)

        self.white_controlled_squares = set(white_controlled_squares)

    def update_black_controlled_squares(self):
        """Create set to determine if white king is in check and limit
        white king moves which would put it in check.
        """
        black_controlled_squares = []

        for piece in self.black_pieces:
            piece.update_moves(self)
            if not isinstance(piece, pieces.Pawn):
                for move in piece.moves:
                    black_controlled_squares.append(move)
            for square in piece.protected_squares:
                black_controlled_squares.append(square)

        self.black_controlled_squares = set(black_controlled_squares)

    def find_sliding_controlled_squares(self, color):
        """Return squares controlled by sliding pieces of given color.
        Use for detecting pins only.
        """
        if color == 'white':
            color_pieces = self.white_pieces
        elif color == 'black':
            color_pieces = self.black_pieces
        else:
            raise ValueError('Invalid piece color')
        sliding_pieces_controlled_squares = []
        for piece in color_pieces:
            if isinstance(piece, (pieces.Bishop, pieces.Rook, pieces.Queen)):
                orig_moves = piece.moves
                piece.update_moves(self)
                for move in piece.moves:
                    sliding_pieces_controlled_squares.append(move)
                piece.moves = orig_moves
        return sliding_pieces_controlled_squares

    def remove_illegal_moves_for_pinned_pieces(self, piece_color):
        """Find and restrict pinned pieces.
        Should be called immediately before their turn.
        """
        if piece_color == 'white':
            color_pieces = self.white_pieces
        else:
            color_pieces = self.black_pieces
        # King cannot be pinned.
        assert isinstance(color_pieces[-1], pieces.King)
        for piece in color_pieces[:-1]:
            # <piece>.is_pinned() calls func. which removes illegal moves
            piece.is_pinned(self)

    def find_checking_pieces(self) -> list:
        """Assume a king is in check based on Board.last_move_piece.color.
        Return which piece(s) is/are checking the king.

        Note that this may be called when checked_square isn't in
        opponent controlled squares, such as when looking for pins.
        """
        # Only one king may be in check at any time.
        if self.last_move_piece.color == 'white':
            checked_king = self.black_king
            opponent_pieces = self.white_pieces
        else:
            checked_king = self.white_king
            opponent_pieces = self.black_pieces

        checked_square = checked_king.square

        checking_pieces = []
        # Should update_moves() notice if the opponent's king is attacked?
        for piece in opponent_pieces:
            if isinstance(piece, pieces.Pawn):
                if checked_square in piece.protected_squares:
                    checking_pieces.append(piece)
            else:
                if checked_square in piece.moves:
                    checking_pieces.append(piece)
        return checking_pieces

    def find_interposition_squares(self, checking_pieces: list,
                                   checked_king) -> list:
        """Assumes a king is in check. Return set of interposition squares
        which block check.

        Helper function for Board.king_escapes_check_or_checkmate().
        """
        interposable_checking_pieces = []
        for piece in checking_pieces:
            if isinstance(piece, (pieces.Bishop, pieces.Rook, pieces.Queen)):
                interposable_checking_pieces.append(piece)
        interposition_squares = []

        for checking_piece in interposable_checking_pieces:
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
                # Indirectly assign move_direction for rest of function.
                for move_direction in range(9, 6, -1):
                    if delta % move_direction == 0:
                        break

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
        interpose_squares = self.find_interposition_squares(
            checking_pieces,
            checked_king)

        # King in double check must move or is in checkmate.
        if len(checking_pieces) > 1:
            if checked_king.moves == []:
                print(f'{checked_king.color.upper()} loses by checkmate.')

        checking_pieces_squares = [piece.square for piece in checking_pieces]

        if checked_king.color == 'white':
            friendly_pieces = board.white_pieces
        else:
            friendly_pieces = board.black_pieces

        # Limit moves for pieces (excluding checked king) to interposition
        # and capturing the checking piece.
        all_legal_moves_in_check = set(interpose_squares
                                       + checking_pieces_squares)

        for piece in friendly_pieces:
            if isinstance(piece, pieces.King):
                continue
            if len(checking_pieces) == 1:
                legal_moves = all_legal_moves_in_check & set(piece.moves)
                piece.moves = list(legal_moves)
                if isinstance(checking_pieces[0], pieces.Pawn) \
                        and isinstance(piece, pieces.Pawn) \
                        and piece.en_passant_move \
                        and abs(checking_pieces[0].square - piece.square) == 1:
                    if piece.color == 'white' \
                            and piece.square in pieces.ranks_files.rank_6 \
                            and checking_pieces[0].square \
                            in pieces.ranks_files.rank_6:
                        piece.moves.append(piece.en_passant_move)
                    elif piece.color == 'black' \
                            and piece.square in pieces.ranks_files.rank_4 \
                            and checking_pieces[0].square \
                            in pieces.ranks_files.rank_4:
                        piece.moves.append(piece.en_passant_move)
            elif len(checking_pieces) > 1:
                piece.moves = []
            else:
                raise ValueError('Length of checking_pieces should be'
                                 ' >= 1')
