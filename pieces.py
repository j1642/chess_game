#import board

class RanksFiles:
    # Certain piece moves are illegal depending on board position. This class
    # prevents redundant creation of these iterables within multiple pieces.
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

        # If x is small, list(range(x)) seems to be faster than comprehensions.
        self.rank_1 = set(range(8))
        self.rank_2 = set(range(8, 16))
        self.rank_3 = set(range(16, 24))
        self.rank_4 = set(range(24, 32))
        self.rank_5 = set(range(32, 40))
        self.rank_6 = set(range(40, 48))
        self.rank_7 = set(range(48, 56))
        self.rank_8 = set(range(56, 64))


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
        return f'''Sym:, {self.symbol}, Sq:, {self.square}, {self.color},
    has_moved: {self.has_moved}'''


    # TODO: Allow diagonal captures, en passant (add sides of board boundary)
    # TODO: Remove moves where a friendly piece is
    def update_moves(self):
        self.moves = []
        if self.has_moved is True:
            if self.color == 'white':
                self.moves.append(self.square + 8)
            elif self.color == 'black':
                self.moves.append(self.square - 8)
        elif self.has_moved is False:
            if self.color == 'white':
                self.moves.append(self.square + 8)
                self.moves.append(self.square + 16)
            elif self.color == 'black':
                self.moves.append(self.square - 8)
                self.moves.append(self.square - 16)
                
                
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            self.has_moved = True
            old_square = self.square
            self.square = new_square
    #        squares[old_square], squares[new_square] = '', self.name
        else:
            return f'Not a valid move for {self.name}.'
    
    # Update global list of piece positions:
    # Where squares is a global list of square contents
    # Get new_square from input in main script
   # def move_piece(self):
    #    if new_square in self.moves:
     #       old_square = self.square
      #      self.square = new_square
       #     squares[old_square], squares[new_square] = ' ', self.name
        #else:
         #   return f'Not a valid move for {self.name}.'


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
        return f'Sym:, {self.symbol}, Sq:, {self.square}, {self.color}'


    # TODO: Remove moves where a friendly piece is
    # Knight movement is very dependent on current square
    def update_moves(self):
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
            
        self.moves = all_moves
        
        
    # Get new_square from input in main script
    # Squares is now an attribute, <board_object>.squares
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
            
            # squares not working
     #       squares[old_square], squares[new_square] = '', self.symbol
        else:
            print(f'Not a valid move for {self.name}.')
            #print(f'Not a valid move for {self.__class__.__name__}.')
            return f'Not a valid move for {self.name}.'


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
        return f'Sym:, {self.symbol}, Sq:, {self.square}, {self.color}'
        
    
    # TODO: Remove moves where friendly pieces are
    # TODO: Remove moves that jump over pieces
    def update_moves(self):
        all_moves = []
        for direction in (-9, -7, 7, 9):
            for diagonal_scalar in range(1, 7):
                new_square = self.square + direction * diagonal_scalar
                if 0 <= new_square <= 63:
                    all_moves.append(new_square)
                    # Do not allow piece to move over the side of the board
                    if new_square in ranks_files.a_file:
                        break
                    elif new_square in ranks_files.h_file:
                        break
                    #elif new_square in opponent_occupied_squares:
                        #break
                    #elif new_square in friendly_occupied-squares:
                        #all_moves.pop()
                        #break
                else:
                    # No use searching past the top or bottom of the board.
                    break

        # if friendly_piece or opponent_piece in direction a or b or c or d:
            # remove moves past the blocking piece
        
        self.moves = all_moves
    
    
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
    #        squares[old_square], squares[new_square] = '', self.name
        else:
            return f'Not a valid move for {self.name}.'


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
        return f'''Sym:, {self.symbol}, Sq:, {self.square}, {self.color}, 
    has_moved: {self.has_moved}'''
        
    
    # TODO: Remove moves where friendly pieces are
    # TODO: Remove moves that jump over pieces
    def update_moves(self):
        all_moves = []
        
        for direction in (-8, -1, 1, 8):
            for vert_horiz_scalar in range(1, 8):
                new_square = self.square + direction * vert_horiz_scalar
                if -1 < new_square < 64:
                    all_moves.append(new_square)
                    if new_square in ranks_files.a_file:
                        break
                    elif new_square in ranks_files.h_file:
                        break
                # Prevent useless calculations.
                else:
                    break
                    
        self.moves = sorted(all_moves)
    
    
    def move_piece(self, new_square: int, castling=False):
        # TODO: update board list
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
                    raise Exception('Rook', rook.name, 'cannot castle to', new_square)
            else:
                raise Exception(f'Castling rook "{self.name}" is illegal. ' \
                                f'Rook "{self.name}" has already moved.')
            
        elif new_square in self.moves:
            old_square, self.square = self.square, new_square
            self.has_moved = True
    #        squares[old_square], squares[new_square] = '', self.name
        else:
            print(f'Not a valid move for {self.name}.')
            return f'Not a valid move for {self.name}.'


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
        return f'Sym:, {self.symbol}, Sq:, {self.square}, {self.color}'
        
    
    # TODO: Remove moves where friendly pieces are
    # TODO: Remove moves that jump over pieces
    # Copied from bishop and rook update_moves()
    def update_moves(self):
        all_moves = []
        # Vertical and horizontal moves in the first half of the tuple.
        # Diagonal directions in the second half of the tuple.
        for direction in (-8, -1, 1, 8, -9, -7, 7, 9):
            for scalar in range(1, 8):
                new_square = self.square + direction * scalar
                if -1 < new_square < 64:
                    all_moves.append(new_square)
                    # Prevent crossing board sides.
                    if new_square in ranks_files.a_file:
                        break
                    elif new_square in ranks_files.h_file:
                        break
                # Prevent move calculations past top or bottom of board.
                else:
                    break
        
        self.moves = all_moves
    
    
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
   #         squares[old_square], squares[new_square] = '', self.name
        else:
            return f'Not a valid move for {self.name}.'


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
        return f'''Sym:, {self.symbol}, Sq:, {self.square}, {self.color}, 
    moved:, {self.has_moved}, in check:, {self.in_check}'''


    # TODO: Remove moves where friendly pieces are
    # TODO: Remove enemy-controlled squares
    def update_moves(self):
        all_moves = []
        directions = [7, 8, 9, -1, 1, -9, -8, -7]
        if self.square in ranks_files.rank_1:
            directions = directions[:5]
        elif self.square in ranks_files.rank_8:
            directions = directions[3:]

        # Separate if/elif for ranks (rows) and files (columns).
        # A piece can be in both the first rank and the H file.
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
            
        for delta in directions:
            new_square = self.square + delta
            if  -1 < new_square < 64:
                all_moves.append(self.square + delta)
        
        # TODO: Finish Castling - get rook to move as well
        # TODO: Does an empty square that is under attack b/w rook and king
        # prevents castling?
        if self.has_moved is False:
            if self.color == 'white' and self.square == 4:
                # Check if castling kingside is possible.
                if white_rook_h.has_moved is False \
                    and board.squares[5] == board.squares[6] == ' ':
                        all_moves.append(6)
                # Check if castling queenside is possible.
                if white_rook_a.has_moved is False \
                    and board.squares[1] == board.squares[2] == ' ':
                        all_moves.append(2)
            elif self.color == 'black' and self.square == 60:
                # Castle kingside
                if black_rook_h.has_moved is False \
                    and board.squares[61] == board.squares[62] == ' ':
                        all_moves.append(62)
                # Castle queenside
                if black_rook_a.has_moved is False \
                    and board.squares[57] == board.squares[58] == ' ':
                        all_moves.append(58)
                        
        # Remove illegal king moves into opponent controlled squares.
        # King cannot willingly move into check.
        #all_moves_set = set(all_moves)
        #all_moves = list(all_moves_set)
       # 
        #if self.color == 'white':
         #   for illegal_move in board.black_controlled_squares():
          #      try:
           #         all_moves.remove(illegal_move)
            #    except ValueError:
             #       continue
                
       # elif self.color == 'black':
        #    for illegal_move in board.white_controlled_squares():
         #       try:
          #          all_moves.remove(illegal_move)
           #     except ValueError:
            #        continue
                
        self.moves = all_moves
    
    
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
            # Check if king is castling.
            if self.has_moved is False:
                if self.color == 'white':
                    if new_square == 2:
                        white_rook_a.move_piece(3, castling=True)
                    elif new_square == 6:
                        white_rook_h.move_piece(5, castling=True)
                elif self.color == 'black':
                    if new_square == 58:
                        black_rook_a.move_piece(59, castling=True)
                    elif new_square == 62:
                        black_rook_h.move_piece(61, castling=True)
                        
            self.has_moved = True
   #         squares[old_square], squares[new_square] = '', self.name
        else:
            print(f'Not a valid move for {self.name}.')
            return f'Not a valid move for {self.name}.'



##############################################################################
# Tests
##############################################################################

if __name__ == '__main__':
    import unittest
    
    # For king testing. Global variables
    class Board:
        def __init__(self):
            self.squares = [' '] * 64
            
    # Globals required for testing.
    board = Board()
    black_rook_a = Rook('ra', 'black', 56)
    black_rook_h = Rook('rh', 'black', 63)
    white_rook_a = Rook('Ra', 'white', 0)
    white_rook_h = Rook('Rh', 'white', 7)
    
    ranks_files = RanksFiles()
    
    
    class TestPieceMovement(unittest.TestCase):
        def test_pawn_movement(self):
            pawn = Pawn('Pa', 'white', 8)
            self.assertFalse(pawn.moves)
            self.assertFalse(pawn.has_moved)
            pawn.update_moves()
            self.assertEqual(pawn.moves, [16, 24])
            pawn.move_piece(24)
            self.assertEqual(pawn.square, 24)
            self.assertTrue(pawn.has_moved)
            pawn.update_moves()
            self.assertEqual(pawn.moves, [32])
            
            pawn = Pawn('ph', 'black', 49)
            pawn.update_moves()
            self.assertEqual(pawn.moves, [41, 33])
            
            
        def test_knight_movement(self):
            knight = Knight('Kb', 'white', 1)
            self.assertFalse(knight.moves)
            knight.update_moves()
            # Change this to exclude d2 at start b/c occupied by friendly pawn.
            self.assertEqual(set(knight.moves), set((16, 18, 11)))
            knight.move_piece(18)
            self.assertEqual(knight.square, 18)
            knight.update_moves()
            knight_move_directions = (-15, -17, -6, -10, 6, 10, 15, 17)
            supposed_knight_moves = [(18 + i) for i in knight_move_directions]
            self.assertEqual(set(knight.moves), set((supposed_knight_moves)))
            
        def test_bishop_movement(self):
            bishop = Bishop('Bc', 'white', 2)
            self.assertFalse(bishop.moves)
            bishop.update_moves()
            supposed_bishop_moves = set((11, 20, 29, 38, 47, 9, 16))
            self.assertEqual(set(bishop.moves), supposed_bishop_moves)
            
            bishop = Bishop('bf', 'black', 52)
            bishop.update_moves()
            supposed_bishop_moves = set((61, 59, 45, 38, 31, 43, 34, 25, 16))
            self.assertEqual(set(bishop.moves), supposed_bishop_moves)
            
        
        def test_rook_movement(self):
            rook = Rook('Ra', 'white', 9)
            self.assertFalse(rook.moves)
            self.assertFalse(rook.has_moved)
            rook.update_moves()
            supposed_rook_moves = [1, 8] + list(range(17, 58, 8)) \
                                + list(range(10, 16))
            self.assertEqual(set(rook.moves), set(supposed_rook_moves))
            rook.move_piece(10)
            self.assertTrue(rook.has_moved)
            
            rook = Rook('Ra', 'white', 0)
            self.assertFalse(rook.moves)
            rook.move_piece(3, castling=True)
            self.assertEqual(rook.square, 3)
            self.assertTrue(rook.has_moved)
            
            rook = Rook('ra', 'black', 56)
            self.assertFalse(rook.moves)
            rook.move_piece(59, castling=True)
            self.assertEqual(rook.square, 59)
            self.assertTrue(rook.has_moved)
            self.assertRaises(Exception, rook.move_piece, 59, castling=True)
            
            rook = Rook('ra', 'white', 0)
            self.assertRaises(Exception, rook.move_piece, 100, castling=True)
            
            
        def test_queen_movement(self):
            queen = Queen('Q', 'white', 9)
            self.assertFalse(queen.moves)
            queen.update_moves()
            # Possible rook moves plus possible bishop moves.
            supposed_queen_moves = [1, 8] + list(range(17, 58, 8)) \
                                + list(range(10, 16))
            supposed_queen_moves += [0, 16, 2, 18, 27, 36, 45, 54, 63]
            self.assertEqual(set(queen.moves), set(supposed_queen_moves))
            
        def test_king_movement(self):
            
            king = King('k', 'black', 63)
            self.assertFalse(king.has_moved)
            self.assertFalse(king.moves)
            # Rooks need to exist to check for castling possibility.
            board = Board()
            king.update_moves()
            self.assertEqual(set(king.moves), set((62, 55, 54)))
            king.move_piece(55)
            self.assertTrue(king.has_moved)
        
            king = King('K', 'white', 4)
            self.assertFalse(king.moves)
            self.assertFalse(king.has_moved)
            king.update_moves()
            self.assertEqual(set(king.moves), set((3, 11, 12, 13, 5, 2, 6)))

            
    unittest.main()