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

# TODO: does piece.move_piece(board) have to return board? Aren't the
# attribute changed in the board object already?

class RanksFiles:
    '''Holds iterables for limiting piece movement.'''
    # Certain movement directions are illegal depending on piece location.
    # E.g. a knight may not jump over the edge of the board.
    
    # Sets have a constant time complexity for membership check, and are not
    # time intensive to create, according to timeit.timeit().
    def __init__(self):
        self.a_file = set([i * 8 for i in range(8)])
        self.b_file = set([i * 8 + 1 for i in range(8)])
        self.c_file = set([i * 8 + 2 for i in range(8)])
        self.d_file = set([i * 8 + 3 for i in range(8)])
        self.e_file = set([i * 8 + 4 for i in range(8)])
        self.f_file = set([i * 8 + 5 for i in range(8)])
        self.g_file = set([i * 8 + 6 for i in range(8)])
        self.h_file = set([i * 8 + 7 for i in range(8)])

        # If x is small, list(range(x)) seems to be slightly faster than list
        # comprehensions.
        self.rank_1 = set(range(8))
        self.rank_2 = set(range(8, 16))
        self.rank_3 = set(range(16, 24))
        self.rank_4 = set(range(24, 32))
        self.rank_5 = set(range(32, 40))
        self.rank_6 = set(range(40, 48))
        self.rank_7 = set(range(48, 56))
        self.rank_8 = set(range(56, 64))
        

ranks_files = RanksFiles()


class Pawn:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.giving_check = False
        
        if self.color == 'white':
            self.symbol = 'P'
        elif self.color == 'black':
            self.symbol = 'p'
        
        
    def __repr__(self):
        return f'''({self.symbol}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved})'''


    # TODO: En passant, with sides of board boundary)
    # Keep record of last move. If last move was a pawn moving two squares
    # forward, en passant is available if there is a pawn on either side of the
    # moved pawns new square.
    def update_moves(self, board):
        '''Update pawn moves.'''
        all_squares = board.squares
        self.moves = []
        forward_direction = 8
        
        if self.color == 'black':
            forward_direction = -8
        
        square_in_front = self.square + forward_direction
        
        if 0 <= square_in_front <= 63:
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
                    
                    
            # Check for valid captures.
            for direction in capture_directions:
                examined_square = self.square + direction
                try:
                    # Check if piece in examined_square is the opponent's.
                    square_contents = all_squares[examined_square].color
                    if square_contents != self.color:
                        # Capturing opponent's piece is a legal move.
                        self.moves.append(examined_square)
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
            self.promote_pawn()
        
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
            print(f'Not a valid move for {self.name}.')
        

class Knight:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False

        if self.color == 'white':
            self.symbol = 'N'
        elif self.color == 'black':
            self.symbol = 'n'


    def __repr__(self):
        return f'({self.symbol}, Sq: {self.square}, {self.color})'


    def update_moves(self, board):
        '''Update knight moves.'''
        all_squares = board.squares
        # Moves ordered by move direction clockwise
        #all_moves = [self.square + delta for delta in [17, 10, -6, -15, -17, -10, 6, 15]]

        # Moves ordered from downward (toward 1st rank) to upward knight movements
        knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
        all_moves = [self.square + delta for delta in knight_move_directions]
        
        if self.square in ranks_files.rank_1:
            del all_moves[:4] # was index 3 (incorrect). Going to 4 correctly removes all neg. moves.
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
        all_moves_copy = all_moves.copy()
        for square in all_moves_copy:
            try:
                square_contents = all_squares[square].color
                if square_contents == self.color:
                    all_moves.remove(square)
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
            #print(f'Not a valid move for {self.__class__.__name__}.')
            

class Bishop:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False
        
        if self.color == 'white':
            self.symbol = 'B'
        elif self.color == 'black':
            self.symbol = 'b'
            
            
    def __repr__(self):        
        return f'({self.symbol}, Sq: {self.square}, {self.color})'
        
    
    def update_moves(self, board):
        '''Update bishop moves.'''
        all_squares = board.squares
        all_moves = []
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
                        # Do not add move.
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
            

class Rook:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.giving_check = False
        
        if self.color == 'white':
            self.symbol = 'R'
        elif self.color == 'black':
            self.symbol = 'r'
            
            
    def __repr__(self):        
        return f'''({self.symbol}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved})'''
        
    
    def update_moves(self, board):
        '''Update rook moves.'''
        all_squares = board.squares
        all_moves = []
        
        for direction in (-8, -1, 1, 8):
            for vert_horiz_scalar in range(1, 8):
                new_square = self.square + direction * vert_horiz_scalar
                if -1 < new_square < 64:
                    # Is new square empty, a friendly piece, or opposing piece?
                    if all_squares[new_square] == ' ':
                        pass
                    elif self.color == all_squares[new_square].color:
                        # Do not add move.
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
        # Do not return board here when castling. Board will be returned by
        # King.move_piece().
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
                    raise Exception('Rook', rook.name, 'cannot castle to', new_square)
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


class Queen:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.giving_check = False
        
        if self.color == 'white':
            self.symbol = 'Q'
        elif self.color == 'black':
            self.symbol = 'q'
            
            
    def __repr__(self):        
        return f'({self.symbol}, Sq: {self.square}, {self.color})'
        
    # Could replace this with bishop.moves + rook.moves from the queen's square
    def update_moves(self, board):
        '''Update queen moves.'''
        all_squares = board.squares
        all_moves = []
        
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
                        # Do not add move.
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
            

class King:
    def __init__(self, name: str, white_or_black: str, position: int):
        self.name = name
        self.color = white_or_black
        self.square = position
        self.moves = []
        self.has_moved = False
        self.in_check = False
        
        if self.color == 'white':
            self.symbol = 'K'
        elif self.color == 'black':
            self.symbol = 'k'
            
            
    def __repr__(self):
        return f'''({self.symbol}, Sq: {self.square}, {self.color}, \
    has_moved: {self.has_moved}, in check: {self.in_check})'''


    def update_moves(self, board):
        all_squares = board.squares
        all_moves = []
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
            except AttributeError:
                assert all_squares[square] == ' '
                continue
        
        # TODO: King cannot castle out of, through, or into check.
        # Done: king cannot castle out of check.
        # Done: king cannot castle through check.
        # Probably done through move removal: king can't castle into check.
        # TIME FOR TESTS!
        
        # Add any possible castling moves to all_moves.
        # This castling block could be less repetitive. No straightforward fix.
        if self.has_moved is False and self.in_check is False:
            if self.color == 'white' and self.square == 4:
                # Check if castling kingside is possible.
                try:
                    supposed_h7_rook_name = all_squares[7].name
                    supposed_h7_rook_has_moved = all_squares[7].has_moved
                    if supposed_h7_rook_name == 'Rh' \
                        and supposed_h7_rook_has_moved is False \
                        and all_squares[5] == all_squares[6] == ' ' \
                        and all_squares[5] not in board.black_controlled_squares \
                        and all_squares[6] not in board.black_controlled_squares:
                            all_moves.append(6)
                except AttributeError:
                    # No assert all_squares[7] == ' ' because there could be a
                    # piece present. Some pieces have a name without having the
                    # has_moved attribute.
                    pass
                
                try:
                    # Check if castling queenside is possible.
                    supposed_a1_rook_name = all_squares[0].name
                    supposed_a1_rook_has_moved = all_squares[0].has_moved
                    if supposed_a1_rook_name == 'Ra' \
                        and supposed_a1_rook_has_moved is False \
                        and all_squares[1] == all_squares[2] == all_squares[3] == ' ' \
                        and all_squares[2] not in board.black_controlled_squares \
                        and all_squares[3] not in board.black_controlled_squares:
                            all_moves.append(2)
                except AttributeError:
                    pass
                
            elif self.color == 'black' and self.square == 60:
                # Check if castling kingside is possible.
                try:
                    supposed_h8_rook_name = all_squares[63].name
                    supposed_h8_rook_has_moved = all_squares[63].has_moved
                    if supposed_h8_rook_name == 'rh' \
                        and supposed_h8_rook_has_moved is False \
                        and all_squares[61] == all_squares[62] == ' ' \
                        and all_squares[61] not in board.white_controlled_squares \
                        and all_squares[62] not in board.white_controlled_squares:
                            all_moves.append(62)
                except AttributeError:
                    pass
                
                # Check if castling queenside is possible.
                try:
                    supposed_a8_rook_name = all_squares[56].name
                    supposed_a8_rook_has_moved = all_squares[56].has_moved
                    if supposed_a8_rook_name == 'ra' \
                        and supposed_a8_rook_has_moved is False \
                        and all_squares[57] == all_squares[58] == all_squares[59] == ' ' \
                        and all_squares[58] not in board.white_controlled_squares \
                        and all_squares[59] not in board.white_controlled_squares:
                            all_moves.append(58)
                except AttributeError:
                    pass
        
        self.moves = all_moves
                
        # Prevent checked king from moving into a square where the king
        # would still be in check, but where the new square was not
        # under attack previously.
        
        # E.g. A checked king moving from e1 to f1 with the opponent's rook
        # on a1 would still be in check.
        if self.in_check:
            board.squares[self.square] = ' '
            if self.color == 'white':
                board.update_black_controlled_squares()
            elif self.color == 'black':
                board.update_white_controlled_squares()
            board.squares[self.square] = self
        
        # Remove illegal moves. If in check, this includes moves that would
        # keep the king in check (implemented in the block above).
        self.remove_moves_to_attacked_squares(board.white_controlled_squares,
                                              board.black_controlled_squares)


    def remove_moves_to_attacked_squares(self, white_controlled_squares: set,
                                         black_controlled_squares: set):
        'Helper method to King.update_moves()'
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
                        white_rook_a = all_squares[0]
                        white_rook_a.move_piece(3, castling=True)
                    elif new_square == 6:
                        white_rook_h = all_squares[7]
                        white_rook_h.move_piece(5, castling=True)
                elif self.color == 'black':
                    if new_square == 58:
                        black_rook_a = all_squares[56]
                        black_rook_a.move_piece(59, castling=True)
                    elif new_square == 62:
                        black_rook_h = all_squares[63]
                        black_rook_h.move_piece(61, castling=True)
                        
            self.has_moved = True
            board.squares[old_square], board.squares[new_square] = ' ', self
        else:
            print(f'Not a valid move for {self.name}.')
            


##############################################################################
# Tests
##############################################################################


if __name__ == '__main__':
    import unittest


    class Board:
        '''Partial board class with limited functionality.'''
        def __init__(self):
            self.squares = [' '] * 64
            self.white_pieces = []
            self.black_pieces = []
            self.white_controlled_squares = []
            self.black_controlled_squares = []
    
    
    # TODO: What's up with this?
    # It seems like there needs to be a global board variable for these tests.
    # Shouldn't a local all_squares variable work without giving a NameError?
    class SetUpTearDown(unittest.TestCase):
        
        def setUp(self):
            global board
            board = Board()
            global all_squares
            all_squares = board.squares
            
        
        def tearDown(self):
            global board
            del board
            global all_squares
            del all_squares
            
            
    class TestPieceMovement(SetUpTearDown):
        
        def test_board_updates_upon_piece_movement(self):
            # The relevant code is in the move_piece method of each piece class.
            self.assertEqual(all_squares, [' '] * 64)
            pawn = Pawn('P', 'white', 0)
            knight = Knight('N', 'white', 1)
            king = King('K', 'white', 2)
            rook = Rook('Ra', 'white', 3)
            queen = Queen('Q', 'white', 4)
            bishop = Bishop('B', 'white', 5)
            
            pieces = (pawn, knight, king, rook, queen, bishop)
            
            for ind, piece in enumerate(pieces):
                board.squares[ind] = piece
                
            self.assertEqual(all_squares[:6], list(pieces))
                
            for piece in pieces:
                    piece.update_moves(board)
            
            # Make sure it is possible to iteratively update the move lists.
            self.assertEqual(pawn.moves, [8, 16])
            
            new_squares = (8, 18, 10, 11, 12, 14)
            for ind, piece in enumerate(pieces):
                piece.move_piece(board, new_squares[ind])
            
            # This test will fail if the new_squares are changed, so it works.
            for ind, piece in enumerate(pieces):
                self.assertEqual(all_squares[new_squares[ind]], piece)
                
        
        def test_pawn_movement(self):
            pawn = Pawn('Pa', 'white', 8)
            self.assertFalse(pawn.moves)
            self.assertFalse(pawn.has_moved)
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [16, 24])
            pawn.move_piece(board, 24)
            self.assertEqual(pawn.square, 24)
            self.assertEqual(board.squares[24], pawn)
            self.assertTrue(pawn.has_moved)
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [32])
            
            pawn = Pawn('ph', 'black', 49)
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [41, 33])
            
            
        def test_blocked_pawn_cannot_move_forward_by_one(self):
            pawn = Pawn('Pa', 'white', 16)
            all_squares[16] = pawn
            
            # Friendly blocking piece.
            blocking_piece = Pawn('Pb', 'white', 24)
            all_squares[24] = blocking_piece
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [])
            
            # Opponent blocking piece.
            blocking_piece = Pawn('q', 'black', 24)
            all_squares[24] = blocking_piece
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [])
            
            
        def test_partially_blocked_pawn_cannot_move_forward_by_two(self):
            pawn = Pawn('Pa', 'white', 16)
            all_squares[16] = pawn
            self.assertFalse(pawn.has_moved)
            
            blocking_piece = King('k', 'black', 32)
            all_squares[32] = blocking_piece
            
            pawn.update_moves(board)
            self.assertEqual(pawn.moves, [24])
            
        
        def test_white_pawn_captures(self):
            pawn = Pawn('Pd', 'white', 11)
            friendly_piece = Bishop('Bc', 'white', 18)
            opponent_piece = Pawn('pe', 'black', 20)
            
            all_squares[11] = pawn
            all_squares[18] = friendly_piece
            all_squares[20] = opponent_piece
            
            pawn.update_moves(board)
            # Pawn should be able to move forward by 1 or 2 squares and
            # capture the enemy pawn.
            self.assertFalse(pawn.has_moved)
            self.assertEqual(set(pawn.moves), set([19, 27, 20]))
            
            
        def test_black_pawn_captures(self):
            pawn = Pawn('pa', 'black', 48)
            friendly_piece = Knight('nb', 'black', 32)
            opponent_piece = Queen('Q', 'white', 41)
            
            all_squares[48] = pawn
            all_squares[32] = friendly_piece
            all_squares[41] = opponent_piece
            
            pawn.update_moves(board)
            # Pawn can move forward by one (not two) or capture opponent queen.
            self.assertFalse(pawn.has_moved)
            self.assertEqual(set(pawn.moves), set([40, 41]))
            
            
        def test_pawn_cannot_capture_past_board_edge(self):
            # If pawn and opponent_pawn_h can capture each other, test will fail.
            pawn = Pawn('Pa', 'white', 8)
            opponent_pawn_b = Pawn('pb', 'black', 17)
            opponent_pawn_h = Pawn('ph', 'black', 15)
            
            opponent_pawn_b.has_moved = True
            opponent_pawn_h.has_moved = True
            
            all_squares[8] = pawn
            all_squares[17] = opponent_pawn_b
            all_squares[15] = opponent_pawn_h
            
            pawn.update_moves(board)
            opponent_pawn_b.update_moves(board)
            opponent_pawn_h.update_moves(board)
            
            self.assertFalse(pawn.has_moved)
            self.assertTrue(opponent_pawn_b.has_moved)
            self.assertTrue(opponent_pawn_h.has_moved)
            
            self.assertEqual(set(pawn.moves), set([16, 24, 17]))
            self.assertEqual(set(opponent_pawn_b.moves), set([9, 8]))
            self.assertEqual(opponent_pawn_h.moves, [7])
            
            
        # TODO
        def test_promote_pawn_walking_down_board(self):
            white_pawn = Pawn('Pa', 'white', 8)
            black_pawn = Pawn('ph', 'black', 63)
            
            board.white_pieces = [white_pawn]
            board.black_pieces = [black_pawn]
            
            while white_pawn.square < 56:
                white_pawn.update_moves(board)
                white_pawn.move_piece(board, white_pawn.moves[0])
                
            while black_pawn.square > 7:
                black_pawn.update_moves(board)
                black_pawn.move_piece(board, black_pawn.moves[0])
                
            white_pawn.update_moves(board)
            black_pawn.update_moves(board)
            
            self.assertTrue(isinstance(board.squares[56], Queen))
            self.assertEqual(board.white_pieces, [board.squares[56]])
            
            self.assertTrue(isinstance(board.squares[7], Queen))
            self.assertEqual(board.black_pieces, [board.squares[7]])
            
            
        def test_promote_pawn_after_capture(self):
            # Test that pawns which just captured a piece are promoted.
            white_pawn = Pawn('Pa', 'white', 48)
            black_pawn = Pawn('pa', 'black', 8)
            white_piece_to_capture = Knight('Nb', 'white', 1)
            black_piece_to_capture = Knight('nb', 'black', 57)
            
            white_pawn.has_moved = True
            black_pawn.has_moved = True
            
            #board = Board()
            board.white_pieces = [white_pawn, white_piece_to_capture]
            board.black_pieces = [black_pawn, black_piece_to_capture]
            for piece in board.white_pieces + board.black_pieces:
                board.squares[piece.square] = piece
            
            white_pawn.update_moves(board)
            black_pawn.update_moves(board)
            self.assertEqual(set(white_pawn.moves), set([56, 57]))
            self.assertEqual(set(black_pawn.moves), set([0, 1]))
                             
            
            white_pawn.move_piece(board, 57)
            black_pawn.move_piece(board, 1)
            
            white_pawn.update_moves(board)
            black_pawn.update_moves(board)
            
            self.assertTrue(isinstance(board.squares[57], Queen))
            self.assertTrue(isinstance(board.squares[1], Queen))
            
            
            
            
        def test_knight_movement(self):
            knight = Knight('Nb', 'white', 1)
            self.assertFalse(knight.moves)
            knight.update_moves(board)
            self.assertEqual(set(knight.moves), set((16, 18, 11)))
            knight.move_piece(board, 18)
            self.assertEqual(knight.square, 18)
            knight.update_moves(board)
            knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
            supposed_knight_moves = [(18 + i) for i in knight_move_directions]
            self.assertEqual(set(knight.moves), set((supposed_knight_moves)))
        
        
        def test_knight_friendly_piece_collision(self):
            knight = Knight('Ng', 'white', 6)
            pawn_e2 = Pawn('Pe', 'white', 12)
            
            all_squares[6] = knight
            all_squares[12] = pawn_e2
            
            knight.update_moves(board)
            # pawn_e2 blocks one possible move from the knight's square.
            self.assertEqual(set(knight.moves), set([21, 23]))
            
            
        def test_knight_capture_available(self):
            knight = Knight('Ng', 'white', 6)
            opponent_piece = Pawn('ph', 'black', 23)
            
            all_squares[6] = knight
            all_squares[23] = opponent_piece
            
            knight.update_moves(board)
            self.assertEqual(set(knight.moves), set([21, 23, 12]))
        
        
        def test_bishop_movement(self):
            bishop = Bishop('Bc', 'white', 2)
            self.assertFalse(bishop.moves)
            bishop.update_moves(board)
            supposed_bishop_moves = set((11, 20, 29, 38, 47, 9, 16))
            self.assertEqual(set(bishop.moves), supposed_bishop_moves)
            
            bishop = Bishop('bf', 'black', 52)
            bishop.update_moves(board)
            supposed_bishop_moves = set((61, 59, 45, 38, 31, 43, 34, 25, 16))
            self.assertEqual(set(bishop.moves), supposed_bishop_moves)
            
            # This block should prevent bishop edge cases on the corners/sides.
            bishop = Bishop('Bc', 'white', 0)
            bishop.update_moves(board)
            self.assertEqual(set(bishop.moves), set(list(range(9, 64, 9))))
            
        def test_bishop_friendly_piece_collision(self):
            bishop = Bishop('Bf', 'white', 7)
            friendly_piece = Rook('Ra', 'white', 35)
            
            all_squares[7] = bishop
            all_squares[35] = friendly_piece
            
            bishop.update_moves(board)
            self.assertEqual(bishop.moves, [14, 21, 28])
            
        
        def test_bishop_opponent_piece_collision(self):
            bishop = Bishop('Bf', 'white', 7)
            opponent_piece = Pawn('pe', 'black', 35)
            
            all_squares[7] = bishop
            all_squares[35] = opponent_piece
            
            bishop.update_moves(board)
            self.assertEqual(bishop.moves, [14, 21, 28, 35])
            
            
        def test_rook_movement(self):
            rook = Rook('Ra', 'white', 9)
            self.assertFalse(rook.moves)
            self.assertFalse(rook.has_moved)
            rook.update_moves(board)
            supposed_rook_moves = [1, 8] + list(range(17, 58, 8)) \
                                + list(range(10, 16))
            self.assertEqual(set(rook.moves), set(supposed_rook_moves))
            rook.move_piece(board, 10)
            self.assertTrue(rook.has_moved)
            
            # This block should prevent any rook edge cases on the corners/sides.
            # I beleive any edge cases here would only result in a duplication
            # of one move in self.moves. May not be important.
            
            # Also, needed to reset board variable because there were a few
            # pieces in it.
            rook = Rook('Ra', 'white', 0)
            rook.update_moves(board)
            self.assertEqual(set(rook.moves), set(list(range(8, 57, 8)) + list(range(1, 8))))
            rook.move_piece(board, 3, castling=True)
            self.assertEqual(rook.square, 3)
            
            rook = Rook('ra', 'black', 56)
            rook.move_piece(board, 59, castling=True)
            self.assertEqual(rook.square, 59)
            self.assertRaises(Exception, rook.move_piece, 59, castling=True)
            
            rook = Rook('Ra', 'white', 0)
            self.assertRaises(Exception, rook.move_piece, 100, castling=True)
            
            
        def test_rook_friendly_piece_collision(self):
            rook = Rook('ra', 'black', 9)
            friendly_knight = Knight('nb', 'black', 57)
            friendly_pawn_a = Pawn('pa', 'black', 8)
            friendly_pawn_c = Pawn('pc', 'black', 10)
            
            all_squares[9] = rook
            all_squares[57] = friendly_knight
            all_squares[8] = friendly_pawn_a
            all_squares[10] = friendly_pawn_c
            
            rook.update_moves(board)
            self.assertEqual(set(rook.moves), set([1] + list(range(17, 50, 8))))
        
        
        def test_rook_opponent_piece_collision(self):
            rook = Rook('ra', 'black', 9)
            opponent_pawn = Pawn('Pc', 'white', 10)
            opponent_knight = Knight('Nb', 'white', 1)
            opponent_rook = Rook('Ra', 'white', 8)
            
            all_squares[9] = rook
            all_squares[10] = opponent_pawn
            all_squares[1] = opponent_knight
            all_squares[8] = opponent_rook
            
            rook.update_moves(board)
            self.assertEqual(set(rook.moves), set([8, 1, 10,] \
                                                  + list(range(17, 58, 8))))
            
        def test_queen_movement(self):
            queen = Queen('Q', 'white', 9)
            self.assertFalse(queen.moves)
            queen.update_moves(board)
            # Possible rook moves plus possible bishop moves.
            supposed_queen_moves = [1, 8] + list(range(17, 58, 8)) \
                                + list(range(10, 16))
            supposed_queen_moves += [0, 16, 2, 18, 27, 36, 45, 54, 63]
            self.assertEqual(set(queen.moves), set(supposed_queen_moves))
            
            # This block should prevent queen edge cases on the corners/sides.
            queen = Queen('Q', 'white', 0)
            queen.update_moves(board)
            self.assertEqual(set(queen.moves), set(list(range(9, 64, 9)) \
                                          + list(range(8, 57, 8)) \
                                          + list(range(1, 8))))
                
        def test_queen_friendly_piece_collision(self):
            queen = Queen('q', 'black', 56)
            friendly_knight = Knight('nb', 'black', 57)
            friendly_pawn = Pawn('pb', 'black', 49)
            
            all_squares[56] = queen
            all_squares[57] = friendly_knight
            all_squares[49] = friendly_pawn
            
            queen.update_moves(board)
            self.assertEqual(set(queen.moves), set(list(range(0, 49, 8))))
        
        
        def test_queen_opponent_piece_collision(self):
            queen = Queen('q', 'black', 0)
            opponent_bishop = Bishop('Bc', 'white', 2)
            opponent_pawn = Pawn('Pb', 'white', 9)
            
            all_squares[0] = queen
            all_squares[2] = opponent_bishop
            all_squares[9] = opponent_pawn
            
            queen.update_moves(board)
            self.assertEqual(set(queen.moves), set([1, 2, 9] \
                                                   + list(range(8, 57, 8))))            
            
        
        # TODO: Explicitly test king castling, make sure rook moves as well
        # and that the Board object updates.
        def test_king_movement(self):
            king = King('k', 'black', 63)
            self.assertFalse(king.has_moved)
            self.assertFalse(king.moves)
            # Rooks need to exist to check for castling possibility.
            king.update_moves(board)
            self.assertEqual(set(king.moves), set((62, 55, 54)))
            king.move_piece(board, 55)
            self.assertTrue(king.has_moved)
            
            # Initialize rooks so king can add castling moves to king.moves.
            all_squares[0] = Rook('Ra', 'white', 0)
            all_squares[7] = Rook('Rh', 'white', 7)
        
            king = King('K', 'white', 4)
            self.assertFalse(king.moves)
            self.assertFalse(king.has_moved)
            king.update_moves(board)
            self.assertEqual(set(king.moves), set((3, 11, 12, 13, 5, 2, 6)))
            
            
        def test_king_friendly_piece_collision(self):
            # Technically, we should set king.has_moved to true.
            # If not doing that affects the outcome of this test, then there
            # is a bug.
            king = King('K', 'white', 12)
            friendly_pawn_e = Pawn('Pe', 'white', 28)
            friendly_pawn_d = Pawn('Pd', 'white', 11)
            friendly_queen = Queen ('Q', 'white', 3)
            friendly_pawn_f = Pawn('Pf', 'white', 13)
            friendly_bishop = Bishop('Bf', 'white', 5)
            
            all_squares[12] = king
            all_squares[28] = friendly_pawn_e
            all_squares[11] = friendly_pawn_d
            all_squares[3] = friendly_queen
            all_squares[13] = friendly_pawn_f
            all_squares[5] = friendly_bishop
            
            king.update_moves(board)
            self.assertEqual(set(king.moves), set([4, 19, 20, 21]))
            
        
        def test_remove_moves_to_attacked_squares(self):
            # Remove king moves into attacked sqaures.
            white_king = King('K', 'white', 4)
            black_king = King('k', 'black', 20)
            black_rook_a = Rook('ra', 'black', 59)
            black_rook_h = Rook('rh', 'black', 61)
            
            all_pieces = (white_king, black_king, black_rook_a,
                          black_rook_h)
                
            for piece in all_pieces:
                board.squares[piece.square] = piece
            
            for piece in all_pieces:
                    piece.update_moves(board)
                
            black_controlled_squares = set(black_rook_a.moves
                                           + black_rook_h.moves
                                           + black_king.moves)
            
            white_controlled_squares = set(white_king.moves)
                
            for king in (white_king, black_king):
                king.remove_moves_to_attacked_squares(white_controlled_squares,
                                                      black_controlled_squares)
            
            self.assertEqual(white_king.moves, [])
            self.assertEqual(set(black_king.moves), set([19, 21, 28, 27, 29]))
            
            
        def test_check_if_in_check(self):
            king = King('K', 'white', 4)
            opponent_rook = Rook('ra', 'black', 0)
            self.assertFalse(king.in_check)
            
            all_squares[4] = king
            all_squares[0] = opponent_rook
            
            king.update_moves(board)
            opponent_rook.update_moves(board)
            
            king.remove_moves_to_attacked_squares(set(king.moves),
                                                  set(opponent_rook.moves))
            king.check_if_in_check(set(king.moves), set(opponent_rook.moves))
            self.assertTrue(king.in_check)
            
        # TODO
        def test_castling(self):
            '''King cannot castle out of, through, or into check.'''
            pass
            
            

            
    unittest.main()