'''
The six chess piece types each have their own class here. The common piece
methods are update_moves() and move_piece(), with more specialized methods
including promote_pawn(), check_if_in_check(), and
remove_moves_to_attacked_squares().

The RanksFiles class acts as iterable storage which assists all of the
update_moves() methods.

Running this file runs approximately 30 unit tests.
'''
# The squares of a chessboard are represented here as integers from 0 to 63.
# Square 0 is the a1 square, which is the bottom-left square from white's
# perspective, and the top-right square from black's perspective.

# The integer values of the squares increase within a rank (row).
# E.g. a1 is square 0, h1 is square 7.

# The values also increase with increasing rank number.
# E.g. a2 is square 8, while a1 is square 0.


# Algebraic notation of the squares.
# | a3 | b3 | c3 | ... | h3 |
# | a2 | b2 | c2 | ... | h2 |
# | a1 | b1 | c1 | ... | h1 |

# Equivalent integer representation.
# | 16 | 17 | 18 | ... | 23 |
# | 8  | 9  | 10 | ... | 15 |
# | 0  | 1  | 2  | ... | 7  |


class RanksFiles:
    '''Holds iterables for limiting piece movement.'''
    # Certain movement directions are illegal depending on piece location.
    # E.g. a knight may not jump over the edge of the board.

    # Sets have a constant time complexity for membership check, and are not
    # time intensive to create, according to timeit.timeit().
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


class Pawn:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.giving_check = False
        self.protected_squares = []


    def __repr__(self):
        return f'''({self.name}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved})'''


    def update_moves(self, board):
        '''Update pawn moves.'''
        all_squares = board.squares
        self.moves = []
        self.protected_squares = []

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


            # Check for valid captures and if pawn is protecting any friendly
            # pieces.
            for direction in capture_directions:
                examined_square = self.square + direction
                try:
                    square_contents = all_squares[examined_square].color
                    if square_contents != self.color:
                        # Capturing opponent's piece is a legal move.
                        self.moves.append(examined_square)
                    elif square_contents == self.color:
                        self.protected_squares.append(examined_square)
                except AttributeError:
                    # examined_square is empty
                    assert all_squares[examined_square] == ' '
                    continue

        # Promote pawn immediately once it reaches its final row.
        else:
            if self.color == 'white' and self.square in list(range(56, 64)):
                self.promote_pawn(board)
            elif self.color == 'black' and self.square in list(range(0, 8)):
                self.promote_pawn(board)


    def add_en_passant_moves(self, board):
        '''Check for any valid en passant captures.

        If the last move was a pawn advancing two squares, check if there are
        any pawns of the opposite color adjacent to the moved pawn's current
        square.
        '''
        last_move_from = board.last_move_from_to[0]
        last_move_to = board.last_move_from_to[1]
        if not isinstance(board.last_move_piece, Pawn):
            return
        elif abs(last_move_from - last_move_to) != 16:
            return
        # Last piece moved was a pawn and it advanced two squares.
        en_passant_squares = []

        if last_move_to in ranks_files.a_file:
            en_passant_squares = [last_move_to + 1]
        elif last_move_to in ranks_files.h_file:
            en_passant_squares = [last_move_to - 1]
        else:
            en_passant_squares = [last_move_to + 1, last_move_to - 1]

        for en_passant_square in en_passant_squares:
            en_passant_piece = board.squares[en_passant_square]
            if isinstance(en_passant_piece, Pawn):
                if board.last_move_piece.color != en_passant_piece.color:
                    #assert self.last_move_piece.square == last_move_to
                    en_passant_piece.moves.append((last_move_from + last_move_to) // 2)


    def promote_pawn(self, board, debug_input='queen'):
        '''Immediately promote pawn when it advances to its final row.'''
        all_squares = board.squares
        if debug_input:
            new_piece_type = debug_input
        else:
            print('\nPawn promotion: which piece should your pawn become?')
            new_piece_type = input('Input queen, rook, bishop, or knight.\n>>> ')
        new_piece_type = new_piece_type.lower()
        if new_piece_type == 'queen':
            all_squares[self.square] = Queen('Q', self.color, self.square)
        elif new_piece_type == 'rook':
            all_squares[self.square] = Rook('R', self.color, self.square)
        elif new_piece_type == 'bishop':
            all_squares[self.square] = Bishop('B', self.color, self.square)
        elif new_piece_type == 'knight':
            all_squares[self.square] = Knight('N', self.color, self.square)
        else:
            print('Unable to interpret your new piece type.')
            self.promote_pawn(board)

        new_piece = all_squares[self.square]

        if self.color == 'white':
            board.white_pieces.append(new_piece)
            board.white_pieces.remove(self)
        elif self.color == 'black':
            new_piece.name = new_piece.name.lower()
            board.black_pieces.append(new_piece)
            board.black_pieces.remove(self)


    def move_piece(self, board, new_square: int):
        '''Move pawn.'''
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

            self.has_moved = True
            old_square, self.square = self.square, new_square
            board.squares[old_square], board.squares[new_square] = ' ', self

        else:
            print(f'Not a valid move for {self.name} (sq: {new_square}).')
            return 'Not a valid move.'


class Knight:
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
        '''Update knight moves.'''
        all_squares = board.squares
        self.protected_squares = []
        # Moves ordered by move direction clockwise
        #all_moves = [self.square + delta for delta in [17, 10, -6, -15, -17,
        #                                              -10, 6, 15]]

        # Moves ordered from downward (toward 1st rank) to upward knight moves
        knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
        all_moves = [self.square + delta for delta in knight_move_directions]

        if self.square in ranks_files.rank_1:
            del all_moves[:4] # was index 3 (incorrect)
        elif self.square in ranks_files.rank_2:
            del all_moves[:2] # was 1, see comment above.
        elif self.square in ranks_files.rank_7:
            del all_moves[6:]
        elif self.square in ranks_files.rank_8:
            del all_moves[4:] # was 3, see comment above.

        # Some of items may be missing due to the the previous del statements.
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
        '''Move knight.'''
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
            board.squares[old_square], board.squares[new_square] = ' ', self

        else:
            print(f'Not a valid move for {self.name}.')
            return 'Not a valid move.'
            #print(f'Not a valid move for {self.__class__.__name__}.')


class Bishop:
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
        '''Update bishop moves.'''
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
                        raise Exception('Square is not empty, however it is' \
                                        'also not occupied by a friendly or ' \
                                        'opponent piece.')

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
        '''Move bishop.'''
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
            board.squares[old_square], board.squares[new_square] = ' ', self

        else:
            print(f'Not a valid move for {self.name}.')
            return 'Not a valid move.'


class Rook:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.giving_check = False
        self.protected_squares = []


    def __repr__(self):
        return f'''({self.name}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved})'''


    def update_moves(self, board):
        '''Update rook moves.'''
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
                        pass
                    elif self.color == all_squares[new_square].color:
                        self.protected_squares.append(new_square)
                        break
                    elif self.color != all_squares[new_square].color:
                        # Rook cannot jump over pieces.
                        all_moves.append(new_square)
                        break
                    else:
                        raise Exception('Square is not empty, however also' \
                                        'is not occupied by a friendly or ' \
                                        'opponent piece.')

                    all_moves.append(new_square)
                    if new_square in ranks_files.a_file and direction == -1:
                        break
                    elif new_square in ranks_files.h_file and direction == 1:
                        break

                # Prevent useless calculations.
                else:
                    # Square is not between 0 and 63, inclusive.
                    break

        self.moves = sorted(all_moves)


    def move_piece(self, board, new_square: int, castling=False):
        '''Move rook.'''
        if castling:
            if not self.has_moved:
                # Do not check if new_square is in self.moves
                if self.color == 'white' and new_square in (3, 5):
                    old_square, self.square = self.square, new_square
                    self.has_moved = True
                elif self.color == 'black' and new_square in (59, 61):
                    old_square, self.square = self.square, new_square
                    self.has_moved = True
                else:
            # Next two exceptions should only appear if castling code has a bug.
                    raise Exception('Rook', self.name, 'cannot castle to', new_square)
            else:
                raise Exception(f'Castling rook "{self.name}" is illegal. ' \
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

            self.has_moved = True
            old_square, self.square = self.square, new_square
            board.squares[old_square], board.squares[new_square] = ' ', self
        else:
            print(f'Not a valid move for {self.name}.')
            return 'Not a valid move.'


class Queen:
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
        '''Update queen moves.'''
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
                        raise Exception('Square is not empty, however also' \
                                        'is not occupied by a friendly or ' \
                                        'opponent piece.')
                    all_moves.append(new_square)
                    # Prevent crossing board sides.
                    if new_square in ranks_files.a_file and direction in (-9, -1, 7):
                        break
                    elif new_square in ranks_files.h_file and direction in (9, 1, -7):
                        break
                # Prevent move calculations past top or bottom of board.
                else:
                    break

        self.moves = all_moves


    def move_piece(self, board, new_square: int):
        '''Move queen.'''
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
            board.squares[old_square], board.squares[new_square] = ' ', self

        else:
            print(f'Not a valid move for {self.name}.')
            return 'Not a valid move.'


class King:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.in_check = False
        self.protected_squares = []


    def __repr__(self):
        return f'''({self.name}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved}, in check: {self.in_check})'''


    def update_moves(self, board):
        '''Update king moves, while considering castling and illegal moves.'''
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
            if  -1 < new_square < 64:
                all_moves.append(self.square + direction)

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
            board.squares[self.square] = ' '
            if self.color == 'white':
                board.update_black_controlled_squares()
            elif self.color == 'black':
                board.update_white_controlled_squares()
            board.squares[self.square] = self

        self.moves = all_moves

        self.add_castling_moves(board)

        # Remove illegal moves. If in check, this includes moves that would
        # keep the king in check (implemented in the block above).
        self.remove_moves_to_attacked_squares(board.white_controlled_squares,
                                              board.black_controlled_squares)



    def add_castling_moves(self, board) -> bool:
        '''Add any possible castling moves to self.moves.'''
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
                if supposed_h7_rook_name == 'Rh' \
                    and supposed_h7_rook_has_moved is False \
                    and all_squares[5] == all_squares[6] == ' ' \
                    and 5 not in board.black_controlled_squares \
                    and 6 not in board.black_controlled_squares:
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
                if supposed_a1_rook_name == 'Ra' \
                    and supposed_a1_rook_has_moved is False \
                    and all_squares[1] == all_squares[2] == all_squares[3] == ' ' \
                    and 2 not in board.black_controlled_squares \
                    and 3 not in board.black_controlled_squares:
                        self.moves.append(2)
                        white_castle_queenside = True
            except AttributeError:
                pass

        elif self.color == 'black' and self.square == 60:
            # Check if castling kingside is possible for black.
            try:
                supposed_h8_rook_name = all_squares[63].name
                supposed_h8_rook_has_moved = all_squares[63].has_moved
                if supposed_h8_rook_name == 'rh' \
                    and supposed_h8_rook_has_moved is False \
                    and all_squares[61] == all_squares[62] == ' ' \
                    and 61 not in board.white_controlled_squares \
                    and 62 not in board.white_controlled_squares:
                        self.moves.append(62)
                        black_castle_kingside = True
            except AttributeError:
                pass

            # Check if castling queenside is possible for black.
            try:
                supposed_a8_rook_name = all_squares[56].name
                supposed_a8_rook_has_moved = all_squares[56].has_moved
                if supposed_a8_rook_name == 'ra' \
                    and supposed_a8_rook_has_moved is False \
                    and all_squares[57] == all_squares[58] == all_squares[59] == ' ' \
                    and 58 not in board.white_controlled_squares \
                    and 59 not in board.white_controlled_squares:
                        self.moves.append(58)
                        black_castle_queenside = True
            except AttributeError:
                pass

        return (white_castle_kingside, white_castle_queenside,
                black_castle_kingside, black_castle_queenside)


    def remove_moves_to_attacked_squares(self, white_controlled_squares: set,
                                         black_controlled_squares: set):
        '''Removes illegal moves into opponent controlled squares from
        King.moves.

        Helper method to King.update_moves().
        '''
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
        '''Check if self (king) is in check.'''
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


    def move_piece(self, board, new_square: int):
        '''Move the king.'''
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
                        white_rook_a.move_piece(3, castling=True)
                    elif new_square == 6:
                        white_rook_h = board.squares[7]
                        white_rook_h.move_piece(5, castling=True)
                elif self.color == 'black':
                    if new_square == 58:
                        black_rook_a = board.squares[56]
                        black_rook_a.move_piece(59, castling=True)
                    elif new_square == 62:
                        black_rook_h = board.squares[63]
                        black_rook_h.move_piece(61, castling=True)

            self.has_moved = True
            board.squares[old_square], board.squares[new_square] = ' ', self
        else:
            print(f'Not a valid move for {self.name}.')
            return 'Not a valid move.'
