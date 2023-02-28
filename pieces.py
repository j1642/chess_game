"""The six chess piece types each have their own class.

The common piece methods are update_moves() and move_piece(), with more
specialized methods including Pawn.promote_pawn(), King.check_if_in_check(),
and King.remove_moves_to_attacked_squares().

The RanksFiles class acts as iterable storage which assists all of the
update_moves() methods.

The squares of a chessboard are represented here as integers from 0 to 63.
Square 0 is the a1 square, which is the bottom-left square from white's
perspective, and the top-right square from black's perspective.

The integer values of the squares increase within a rank (row).
E.g. a1 is square 0, h1 is square 7.

The values also increase with increasing rank number.
E.g. a2 is square 8, while a1 is square 0.

Algebraic notation of the squares.
| a8 | b8 | c8 | ... | h8 |
| .. | .. | .. | ... | .. |
| a3 | b3 | c3 | ... | h3 |
| a2 | b2 | c2 | ... | h2 |
| a1 | b1 | c1 | ... | h1 |

Equivalent integer representation.
| 56 | 57 | 58 | ... | 63 |
| .. | .. | .. | ... | .. |
| 16 | 17 | 18 | ... | 23 |
| 8  | 9  | 10 | ... | 15 |
| 0  | 1  | 2  | ... | 7  |
"""


class RanksFiles:
    """Holds iterables for limiting piece movement."""

    def __init__(self):
        self.a_file = {i * 8 for i in range(8)}
        self.b_file = {i * 8 + 1 for i in range(8)}
        self.c_file = {i * 8 + 2 for i in range(8)}
        self.d_file = {i * 8 + 3 for i in range(8)}
        self.e_file = {i * 8 + 4 for i in range(8)}
        self.f_file = {i * 8 + 5 for i in range(8)}
        self.g_file = {i * 8 + 6 for i in range(8)}
        self.h_file = {i * 8 + 7 for i in range(8)}

        self.files = (self.a_file, self.b_file, self.c_file, self.d_file,
                      self.e_file, self.f_file, self.g_file, self.h_file)

        # Here, set(range()) seems to be slightly faster than set
        # comprehensions.
        self.rank_1 = set(range(8))
        self.rank_2 = set(range(8, 16))
        self.rank_3 = set(range(16, 24))
        self.rank_4 = set(range(24, 32))
        self.rank_5 = set(range(32, 40))
        self.rank_6 = set(range(40, 48))
        self.rank_7 = set(range(48, 56))
        self.rank_8 = set(range(56, 64))

        self.ranks = (self.rank_1, self.rank_2, self.rank_3, self.rank_4,
                      self.rank_5, self.rank_6, self.rank_7, self.rank_8)


ranks_files = RanksFiles()


class _Piece:
    """Superclass only. Do not instantiate.

    Methods
    -------
    is_pinned()
    restrict_moves_when_pinned()
    update_board_after_move()

    """

    # This drastically increases the calculations per turn, but does not
    # noticeably slow test times or computer response time in game.
    # Hypothetical optimization 1: remove all pieces/pawns besides king
    #   and check if king is in check. If True, there may be a pin, so
    #   check if each individual piece is pinned.
    def is_pinned(self, chessboard):
        """Detect if a piece is pinned. If pinned, remove illegal moves."""
        chessboard.squares[self.square] = ' '
        if self.color == 'white':
            friendly_king = chessboard.white_king
            chessboard.update_black_controlled_squares()
        else:
            friendly_king = chessboard.black_king
            chessboard.update_white_controlled_squares()
        chessboard.squares[self.square] = self

        orig_in_check = friendly_king.in_check
        if friendly_king.check_if_in_check(
                chessboard.white_controlled_squares,
                chessboard.black_controlled_squares):
            friendly_king.in_check = orig_in_check
            self.restrict_moves_when_pinned(chessboard, friendly_king)
            return True
        else:
            return False

    def restrict_moves_when_pinned(self, chessboard, friendly_king):
        """Remove illegal moves for a pinned piece."""
        # Does not affect <piece>.protected_squares.
        # While protected squares only limit King moves, this is fine.
        # If protected squares gain responsibilities, this is an issue.
        checking_pieces = chessboard.find_checking_pieces()
        if len(checking_pieces) > 1:
            self.moves = []
            return
        checking_piece_sqrs = [piece.square for piece in checking_pieces]
        interpose_or_capture_sqrs = chessboard.find_interposition_squares(
            checking_pieces,
            friendly_king)
        interpose_or_capture_sqrs = set(
            interpose_or_capture_sqrs
            + checking_piece_sqrs)
        self.moves = list(interpose_or_capture_sqrs & set(self.moves))

    def update_board_after_move(self, chessboard, new_sq, old_sq):
        chessboard.last_move_piece = self
        chessboard.last_move_from_to = (old_sq, new_sq)
        chessboard.squares[old_sq], chessboard.squares[new_sq] = ' ', self


class Pawn(_Piece):
    """The pawn piece.

    Methods
    -------
        __init__()
        __repr__()
        is_pinned()
        update_moves()
        add_en_passant_moves()
        promote_pawn()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.en_passant_move = None
        self.has_moved = False
        self.giving_check = False
        self.protected_squares = []
        self.autopromote = False

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color}, ' \
            f'has_moved: {self.has_moved})'

    def is_pinned(self, chessboard):
        """If not pinned (excluding en passant), remove en passant moves if
        illegal.
        """
        if super().is_pinned(chessboard):
            return True
        if self.en_passant_move is None:
            return False
        capturable_pawn = chessboard.squares[chessboard.last_move_from_to[1]]
        chessboard.squares[self.square] = ' '
        chessboard.squares[capturable_pawn.square] = ' '
        last_move_from, last_move_to = chessboard.last_move_from_to
        en_passant_square = (last_move_from + last_move_to) // 2
        assert chessboard.squares[en_passant_square] == ' '
        chessboard.squares[en_passant_square] = self
        if self.color == 'white':
            friendly_king = chessboard.white_king
            chessboard.update_black_controlled_squares()
        else:
            friendly_king = chessboard.black_king
            chessboard.update_white_controlled_squares()
        if friendly_king.check_if_in_check(
                chessboard.white_controlled_squares,
                chessboard.black_controlled_squares):
            self.moves.remove(self.en_passant_move)
            self.en_passant_move = None
        chessboard.squares[self.square] = self
        chessboard.squares[capturable_pawn.square] = capturable_pawn
        chessboard.squares[en_passant_square] = ' '
        return False

    def update_moves(self, board):
        """Update pawn moves."""
        all_squares = board.squares
        self.moves = []
        self.protected_squares = []
        self.en_passant_move = None

        forward_direction = 8
        if self.color == 'black':
            forward_direction = -8

        square_in_front = self.square + forward_direction

        if 0 <= square_in_front <= 63:
            self.add_en_passant_moves(board)
            # Prevent forward moves if there is a piece blocking the way.
            if all_squares[square_in_front] == ' ':
                if self.has_moved:
                    self.moves.append(square_in_front)
                elif self.has_moved is False:
                    self.moves.append(square_in_front)
                    two_squares_ahead = square_in_front + forward_direction
                    if all_squares[two_squares_ahead] == ' ':
                        self.moves.append(two_squares_ahead)

            # Limit capture directions if pawn is in the A or H file.
            if self.square in ranks_files.a_file:
                if self.color == 'white':
                    capture_directions = (9,)
                elif self.color == 'black':
                    capture_directions = (-7,)
            elif self.square in ranks_files.h_file:
                if self.color == 'white':
                    capture_directions = (7,)
                elif self.color == 'black':
                    capture_directions = (-9,)
            else:
                if self.color == 'white':
                    capture_directions = (7, 9)
                elif self.color == 'black':
                    capture_directions = (-7, -9)

            # Check for valid captures and protected squares.
            for direction in capture_directions:
                diagonal_square = self.square + direction
                self.protected_squares.append(diagonal_square)
                try:
                    square_contents = all_squares[diagonal_square].color
                    if square_contents != self.color:
                        # Capturing opponent's piece is a legal move.
                        self.moves.append(diagonal_square)
                except AttributeError:
                    assert all_squares[diagonal_square] == ' '
                    continue
        else:
            raise TypeError('Pawn should not exist on final rank.')

    def add_en_passant_moves(self, board):
        """Check for any valid en passant captures.

        If the last move was a pawn advancing two squares, check if there
        are any pawns of the opposite color adjacent to the moved pawn's
        current square.
        """
        if board.last_move_from_to == (None, None):
            return
        last_move_from, last_move_to = board.last_move_from_to
        try:
            if not isinstance(board.last_move_piece, Pawn):
                return
            elif abs(last_move_from - last_move_to) != 16:
                return
        except TypeError:
            print('TypeError in Pawn.add_en_passant_moves(). Possibly caused',
                  'by chessboard.last_move_from_to being (None, None).',
                  f'last_move_from={last_move_from}',
                  f'last_move_to={last_move_to}')
        # Last piece moved was a pawn and it advanced two squares.
        en_passant_squares = []
        if last_move_to in ranks_files.a_file:
            en_passant_squares = [last_move_to + 1]
        elif last_move_to in ranks_files.h_file:
            en_passant_squares = [last_move_to - 1]
        else:
            # If the following line causes a TypeError, check that
            # Board.last_move_from_to is not None.
            en_passant_squares = [last_move_to + 1, last_move_to - 1]

        for attacker_square in en_passant_squares:
            if self.square == attacker_square:
                if board.last_move_piece.color != self.color:
                    ep_square = (last_move_from + last_move_to) // 2
                    self.moves.append(ep_square)
                    self.en_passant_move = ep_square

    def promote_pawn(self, board, promote_to=None):
        """Immediately promote pawn when it advances to its final row."""
        all_squares = board.squares
        if promote_to:
            new_piece_type = promote_to
        elif self.autopromote:
            new_piece_type = 'queen'
        else:
            new_piece_type = input('\nPawn promotion: which piece should your '
                                   'pawn become?\nInput queen, rook. bishop, '
                                   'or knight.\n>>> ').lower()
        if new_piece_type == 'queen':
            all_squares[self.square] = Queen('Qp', self.color, self.square)
        elif new_piece_type == 'rook':
            all_squares[self.square] = Rook('Rp', self.color, self.square)
        elif new_piece_type == 'bishop':
            all_squares[self.square] = Bishop('Bp', self.color, self.square)
        elif new_piece_type == 'knight':
            all_squares[self.square] = Knight('Np', self.color, self.square)
        else:
            print('Invalid piece type entered.')
            return self.promote_pawn(board)

        new_piece = all_squares[self.square]

        # King pieces must always be final item in board.<color>_pieces.
        # Insert into board.<color>_pieces, never append.
        if self.color == 'white':
            board.white_pieces.insert(0, new_piece)
            board.white_pieces.remove(self)
        elif self.color == 'black':
            new_piece.name = new_piece.name.lower()
            board.black_pieces.insert(0, new_piece)
            board.black_pieces.remove(self)

    def move_piece(self, board, new_square, promote_to=None):
        """Move the pawn.

        Parameters
        ----------
        board : board.Board

        new_square : int or tuple (int, str)
            Square to move to, or (square to move to, type to promote to)

        promote_to : None or str
            Piece type to promote to, if promoting. Ex: 'queen'

        """
        if isinstance(new_square, tuple) and len(new_square) == 2:
            new_square, promote_to = new_square
            if any([not isinstance(new_square, int),
                    not isinstance(promote_to, str)]):
                raise TypeError("invalid type in 'new_square'")
        elif not isinstance(new_square, int):
            raise TypeError("invalid 'new_square' type")

        if new_square in self.moves:
            captured_piece = None
            if new_square == self.en_passant_move:
                captured_piece_square = board.last_move_from_to[1]
                captured_piece = board.squares[captured_piece_square]
                assert isinstance(captured_piece, Pawn)
                en_passant = True

            elif isinstance(board.squares[new_square],
                            (Pawn, Knight, Bishop, Rook, Queen)):
                captured_piece = board.squares[new_square]
                en_passant = False

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')
            if captured_piece:
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)
                if en_passant:
                    board.squares[captured_piece_square] = ' '

            self.has_moved = True
            old_square, self.square = self.square, new_square
            self.update_board_after_move(board, new_square, old_square)

            if self.color == 'white' and self.square in list(range(56, 64)):
                self.promote_pawn(board, promote_to)
                board.last_move_piece = board.squares[new_square]
            elif self.color == 'black' and self.square in list(range(0, 8)):
                self.promote_pawn(board, promote_to)
                board.last_move_piece = board.squares[new_square]

        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'


class Knight(_Piece):
    """The knight piece.

    Methods
    -------
        __init__()
        __repr__()
        update_moves()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False
        self.protected_squares = []

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color})'

    def update_moves(self, board):
        """Update knight moves."""
        all_squares = board.squares
        self.protected_squares = []
        # Moves ordered from downward (toward 1st rank) to upward knight moves
        knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
        all_moves = [self.square + delta for delta in knight_move_directions]

        if self.square in ranks_files.rank_1:
            all_moves = all_moves[4:]
        elif self.square in ranks_files.rank_2:
            all_moves = all_moves[2:]
        elif self.square in ranks_files.rank_7:
            all_moves = all_moves[:6]
        elif self.square in ranks_files.rank_8:
            all_moves = all_moves[:4]

        if self.square in ranks_files.a_file:
            for movement in (-17, -10, 6, 15):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in ranks_files.b_file:
            for movement in (-10, 6):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in ranks_files.g_file:
            for movement in (10, -6):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in ranks_files.h_file:
            for movement in (17, 10, -6, -15):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue

        # Remove moves where there is a friendly piece.
        # Add these moves to protected_squares attribute.
        all_moves_copy = all_moves.copy()
        for square in all_moves_copy:
            try:
                square_contents = all_squares[square].color
                if square_contents == self.color:
                    all_moves.remove(square)
                    self.protected_squares.append(square)
            except AttributeError:
                assert all_squares[square] == ' '
                continue

        self.moves = all_moves

    def move_piece(self, board, new_square: int):
        """Move the knight."""
        if new_square in self.moves:
            if isinstance(board.squares[new_square], (Pawn, Knight, Bishop,
                                                      Rook, Queen)):
                captured_piece = board.squares[new_square]
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')

            old_square, self.square = self.square, new_square
            self.update_board_after_move(board, new_square, old_square)

        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'


class Bishop(_Piece):
    """The bishop piece.

    Methods
    -------
        __init__()
        __repr__()
        update_moves()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False
        self.protected_squares = []

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color})'

    def update_moves(self, board):
        """Update bishop moves."""
        all_squares = board.squares
        all_moves = []
        self.protected_squares = []

        directions = [9, -7, -9, 7]
        if self.square in ranks_files.a_file:
            directions = directions[:2]
        elif self.square in ranks_files.h_file:
            directions = directions[2:]

        for direction in directions:
            for diagonal_scalar in range(1, 8):
                new_square = self.square + direction * diagonal_scalar
                if -1 < new_square < 64:
                    # Is new square empty, a friendly piece, or opposing piece?
                    if all_squares[new_square] == ' ':
                        pass
                    elif self.color == all_squares[new_square].color:
                        self.protected_squares.append(new_square)
                        break
                    elif self.color != all_squares[new_square].color:
                        # Bishop cannot jump over pieces.
                        all_moves.append(new_square)
                        break
                    else:
                        raise Exception('Square is not empty, but it is'
                                        'also not occupied by a friendly '
                                        'or opponent piece.')

                    all_moves.append(new_square)
                    # Do not allow piece to move over the side of the board.
                    if new_square in ranks_files.a_file:
                        break
                    elif new_square in ranks_files.h_file:
                        break
                else:
                    # No use searching past the top or bottom of the board.
                    break

        # if friendly_piece or opponent_piece in direction a or b or c or d:
            # remove moves past the blocking piece

        self.moves = all_moves

    def move_piece(self, board, new_square: int):
        """Move bishop."""
        if new_square in self.moves:
            if isinstance(board.squares[new_square], (Pawn, Knight, Bishop,
                                                      Rook, Queen)):
                captured_piece = board.squares[new_square]
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')

            old_square, self.square = self.square, new_square
            self.update_board_after_move(board, new_square, old_square)

        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'


class Rook(_Piece):
    """The rook piece.

    Methods
    -------
        __init__()
        __repr__()
        update_moves()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.giving_check = False
        self.protected_squares = []

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color}, ' \
            f'has_moved: {self.has_moved})'

    def update_moves(self, board):
        """Update rook moves."""
        all_squares = board.squares
        all_moves = []
        self.protected_squares = []

        directions = (-8, -1, 1, 8)
        if self.square in ranks_files.a_file:
            directions = (-8, 1, 8)
        elif self.square in ranks_files.h_file:
            directions = (-8, -1, 8)

        for direction in directions:
            for vert_horiz_scalar in range(1, 8):
                new_square = self.square + direction * vert_horiz_scalar
                if -1 < new_square < 64:
                    # Is new square empty, a friendly piece, or opposing piece?
                    if all_squares[new_square] == ' ':
                        all_moves.append(new_square)
                    elif self.color == all_squares[new_square].color:
                        self.protected_squares.append(new_square)
                        break
                    elif self.color != all_squares[new_square].color:
                        # Rook cannot jump over pieces.
                        all_moves.append(new_square)
                        break
                    else:
                        raise Exception('Square is not empty, but also is'
                                        ' not occupied by a friendly or '
                                        'opponent piece.')

                    if new_square in ranks_files.a_file and direction == -1:
                        break
                    elif new_square in ranks_files.h_file and direction == 1:
                        break

                # Square is not between 0 and 63, inclusive.
                else:
                    break

        self.moves = all_moves

    def move_piece(self, board, new_square: int, castling=False):
        """Move rook."""
        if castling:
            if not self.has_moved:
                # Do not check if new_square is in self.moves
                if self.color == 'white' and new_square in (3, 5):
                    old_square, self.square = self.square, new_square
                elif self.color == 'black' and new_square in (59, 61):
                    old_square, self.square = self.square, new_square
                # Next two exceptions should only appear if castling code
                # has a bug.
                else:
                    raise Exception('Rook', self.name, 'cannot castle to',
                                    new_square)
            else:
                raise Exception(f'Castling rook "{self.name}" is illegal. '
                                f'Rook "{self.name}" has already moved.')

        elif new_square in self.moves:
            if isinstance(board.squares[new_square], (Pawn, Knight, Bishop,
                                                      Rook, Queen)):
                captured_piece = board.squares[new_square]
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')
            old_square, self.square = self.square, new_square
        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'

        self.has_moved = True
        self.update_board_after_move(board, new_square, old_square)


class Queen(_Piece):
    """The queen piece.

    Methods
    -------
        __init__()
        __repr__()
        update_moves()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False
        self.protected_squares = []

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color})'

    # Could replace this with bishop.moves + rook.moves from the queen's square
    def update_moves(self, board):
        """Update queen moves."""
        all_squares = board.squares
        all_moves = []
        self.protected_squares = []

        # Prevent jumping from the A-file to H-file, vice versa.
        directions = [9, -7, 1, 8, -8, -1, 7, -9]
        if self.square in ranks_files.a_file:
            directions = directions[:5]
        elif self.square in ranks_files.h_file:
            directions = directions[3:]

        for direction in directions:
            for scalar in range(1, 8):
                new_square = self.square + direction * scalar
                if -1 < new_square < 64:
                    # Is new square empty, a friendly piece, or opposing piece?
                    if all_squares[new_square] == ' ':
                        pass
                    elif self.color == all_squares[new_square].color:
                        self.protected_squares.append(new_square)
                        break
                    elif self.color != all_squares[new_square].color:
                        # Queen cannot jump over pieces.
                        all_moves.append(new_square)
                        break
                    else:
                        raise Exception('Square is not empty, but is '
                                        'not occupied by a friendly or '
                                        'opponent piece.')
                    all_moves.append(new_square)
                    # Prevent crossing board sides.
                    if new_square in ranks_files.a_file \
                            and direction in (-9, -1, 7):
                        break
                    elif new_square in ranks_files.h_file \
                            and direction in (9, 1, -7):
                        break
                # Prevent move calculations past top or bottom of board.
                else:
                    break

        self.moves = all_moves

    def move_piece(self, board, new_square: int):
        """Move queen."""
        if new_square in self.moves:
            if isinstance(board.squares[new_square], (Pawn, Knight, Bishop,
                                                      Rook, Queen)):
                captured_piece = board.squares[new_square]
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')

            old_square, self.square = self.square, new_square
            self.update_board_after_move(board, new_square, old_square)

        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'


class King:
    """The king piece.

    Methods
    -------
        __init__()
        __repr__()
        update_moves()
        add_castling_moves()
        remove_moves_to_attacked_squares()
        check_if_in_check()
        update_board_after_move()
        move_piece()

    """

    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.in_check = False
        self.protected_squares = []

    def __repr__(self):
        return f'({self.name}, Sq: {self.square}, {self.color}, '\
            f'has_moved: {self.has_moved}, in check: {self.in_check})'

    def update_moves(self, board):
        """Update king moves, while considering castling and illegal moves."""
        all_squares = board.squares
        all_moves = []
        self.protected_squares = []

        directions = [7, 8, 9, -1, 1, -9, -8, -7]

        # Separate if/elif for ranks (rows) and files (columns).
        # A piece can be in both the first rank and the H file.
        if self.square in ranks_files.rank_1:
            directions = directions[:5]
        elif self.square in ranks_files.rank_8:
            directions = directions[3:]

        if self.square in ranks_files.a_file:
            for direction in (7, -1, -9):
                try:
                    directions.remove(direction)
                except ValueError:
                    continue
        elif self.square in ranks_files.h_file:
            for direction in (9, 1, -7):
                try:
                    directions.remove(direction)
                except ValueError:
                    continue

        for direction in directions:
            new_square = self.square + direction
            if -1 < new_square < 64:
                all_moves.append(self.square + direction)

        self.protected_squares = all_moves.copy()

        # Remove moves where a friendly piece is. Castling checks this within
        # its own block.
        all_moves_copy = all_moves.copy()
        for square in all_moves_copy:
            try:
                if all_squares[square].color == self.color:
                    all_moves.remove(square)
                    self.protected_squares.append(square)
            except AttributeError:
                assert all_squares[square] == ' '
                continue

        # Prevent checked king from moving into a square where the king
        # would still be in check, but where the new square was not
        # under attack previously.

        # E.g. A checked king moving from e1 to f1 with the opponent's rook
        # on a1 would still be in check.
        if self.check_if_in_check(board.white_controlled_squares,
                                  board.black_controlled_squares):
            checking_pieces = board.find_checking_pieces()

            board.squares[self.square] = ' '
            if self.color == 'white':
                board.update_black_controlled_squares()
            elif self.color == 'black':
                board.update_white_controlled_squares()
            board.squares[self.square] = self

            # If a pawn is checking the king, the pawn cannot detect the
            # "invisible" checked king when the pawn's moves are updated in the
            # block above.
            if checking_pieces:
                for checking_piece in checking_pieces:
                    checking_piece.moves.append(self.square)

                board.moves_must_escape_check_or_checkmate(board, self,
                                                           checking_pieces)

        self.moves = all_moves

        self.add_castling_moves(board)

        # Remove illegal moves. If in check, this includes moves that would
        # keep the king in check (implemented in the block above).
        self.remove_moves_to_attacked_squares(board.white_controlled_squares,
                                              board.black_controlled_squares)

    def add_castling_moves(self, board) -> bool:
        """Add any possible castling moves to self.moves."""
        # Could be less repetitive. What is the straightforward fix?
        all_squares = board.squares

        if self.has_moved or self.in_check:
            return

        # Booleans and contents of return statements for
        # chess_utilities.export_board_to_FEN().
        white_castle_queenside = False
        white_castle_kingside = False
        black_castle_queenside = False
        black_castle_kingside = False

        if self.color == 'white' and self.square == 4:
            # Check if castling kingside is possible for white.
            try:
                supposed_h7_rook_name = all_squares[7].name
                supposed_h7_rook_has_moved = all_squares[7].has_moved
                if all([supposed_h7_rook_name[0] == 'R',
                        supposed_h7_rook_has_moved is False,
                        all_squares[5] == all_squares[6] == ' ',
                        5 not in board.black_controlled_squares,
                        6 not in board.black_controlled_squares]):
                    self.moves.append(6)
                    white_castle_kingside = True
            except AttributeError:
                # No assert all_squares[7] == ' ' because there could be a
                # piece present. Some pieces have a name without having the
                # has_moved attribute.
                pass

            try:
                # Check if castling queenside is possible for white.
                supposed_a1_rook_name = all_squares[0].name
                supposed_a1_rook_has_moved = all_squares[0].has_moved
                if all([supposed_a1_rook_name[0] == 'R',
                        supposed_a1_rook_has_moved is False,
                        all_squares[1] == all_squares[2],
                        all_squares[1] == all_squares[3] == ' ',
                        2 not in board.black_controlled_squares,
                        3 not in board.black_controlled_squares]):
                    self.moves.append(2)
                    white_castle_queenside = True
            except AttributeError:
                pass

        elif self.color == 'black' and self.square == 60:
            # Check if castling kingside is possible for black.
            try:
                supposed_h8_rook_name = all_squares[63].name
                supposed_h8_rook_has_moved = all_squares[63].has_moved
                if all([supposed_h8_rook_name[0] == 'r',
                        supposed_h8_rook_has_moved is False,
                        all_squares[61] == all_squares[62] == ' ',
                        61 not in board.white_controlled_squares,
                        62 not in board.white_controlled_squares]):
                    self.moves.append(62)
                    black_castle_kingside = True
            except AttributeError:
                pass

            # Check if castling queenside is possible for black.
            try:
                supposed_a8_rook_name = all_squares[56].name
                supposed_a8_rook_has_moved = all_squares[56].has_moved
                if all([supposed_a8_rook_name[0] == 'r',
                        supposed_a8_rook_has_moved is False,
                        all_squares[57] == all_squares[58],
                        all_squares[57] == all_squares[59] == ' ',
                        58 not in board.white_controlled_squares,
                        59 not in board.white_controlled_squares]):
                    self.moves.append(58)
                    black_castle_queenside = True
            except AttributeError:
                pass

        return (white_castle_kingside, white_castle_queenside,
                black_castle_kingside, black_castle_queenside)

    def remove_moves_to_attacked_squares(self, white_controlled_squares: set,
                                         black_controlled_squares: set):
        """Remove illegal moves into opponent controlled squares from
        King.moves.

        Helper method to King.update_moves().
        """
        # Remove illegal king moves into opponent controlled squares.
        # King cannot willingly move into check.
        if self.color == 'white':
            opponent_controlled_squares = black_controlled_squares
        elif self.color == 'black':
            opponent_controlled_squares = white_controlled_squares

        moves_copy = self.moves.copy()
        for move in moves_copy:
            if move in opponent_controlled_squares:
                self.moves.remove(move)

    def check_if_in_check(self, white_controlled_squares: set,
                          black_controlled_squares: set):
        """Check if self (king) is in check."""
        if self.color == 'white':
            opponent_controlled_squares = black_controlled_squares
        elif self.color == 'black':
            opponent_controlled_squares = white_controlled_squares

        if self.square in opponent_controlled_squares:
            self.in_check = True
            return True
        else:
            self.in_check = False
            return False

    def update_board_after_move(self, chessboard, new_sq, old_sq):
        """Update Board after move. Must mirror the _Piece function."""
        chessboard.last_move_piece = self
        chessboard.last_move_from_to = (old_sq, new_sq)
        chessboard.squares[old_sq], chessboard.squares[new_sq] = ' ', self

    def move_piece(self, board, new_square: int):
        """Move the king."""
        if new_square in self.moves:
            if isinstance(board.squares[new_square], (Pawn, Knight, Bishop,
                                                      Rook, Queen)):
                captured_piece = board.squares[new_square]
                assert captured_piece.color != self.color
                if self.color == 'white':
                    board.black_pieces.remove(captured_piece)
                elif self.color == 'black':
                    board.white_pieces.remove(captured_piece)

            elif isinstance(board.squares[new_square], King):
                raise Exception('King should not be able to be captured.')

            old_square, self.square = self.square, new_square

            # Check if king is castling. If so, move the corresponding rook.
            # Validity of castling controlled in King.update_moves().
            if self.has_moved is False:
                if self.color == 'white':
                    if new_square == 2:
                        white_rook_a = board.squares[0]
                        white_rook_a.move_piece(board, 3, castling=True)
                    elif new_square == 6:
                        white_rook_h = board.squares[7]
                        white_rook_h.move_piece(board, 5, castling=True)
                elif self.color == 'black':
                    if new_square == 58:
                        black_rook_a = board.squares[56]
                        black_rook_a.move_piece(board, 59, castling=True)
                    elif new_square == 62:
                        black_rook_h = board.squares[63]
                        black_rook_h.move_piece(board, 61, castling=True)

            self.has_moved = True
            self.update_board_after_move(board, new_square, old_square)
        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'
