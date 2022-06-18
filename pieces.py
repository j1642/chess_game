#import board

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

    # TODO: Allow diagonal captures, en passant
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
        # In commented out all_moves, ordered by move direction clockwise
        #all_moves = [self.square + delta for delta in [17, 10, -6, -15, -17, -10, 6, 15]]

        # all_moves ordered by downward (toward 1st rank) to upward knight movements
        all_moves = [self.square + delta for delta in (-15, -17, -6, -10, 6, 10, 15, 17)]
        if self.square in board.rank_1:
            del all_moves[:3]
        elif self.square in board.rank_2:
            del all_moves[:1]
        elif self.square in board.rank_7:
            del all_moves[6:]
        elif self.square in board.rank_8:
            del all_moves[3:]
            
        # Some of list elements may be missing already from del statements.
        if self.square in board.a_file:
            for movement in (-17, -10, 6, 15):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in board.b_file:
            for movement in (-10, 6):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in board.g_file:
            for movement in (10, -6):
                try:
                    all_moves.remove(self.square + movement)
                except ValueError:
                    continue
        elif self.square in board.h_file:
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
            print(f'Not a valid move for {self.__class__.__name__}.')
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
        # Switch these with board_obj attributes later on.
        a_file = [i * 8 for i in range(8)]
        h_file = [i * 8 + 7 for i in range(8)]
        all_moves = []
        for direction in (-9, -7, 7, 9):
            for diagonal_scalar in range(1, 7):
                new_square = self.square + direction * diagonal_scalar
                if 0 <= new_square <= 63:
                    all_moves.append(self.square + direction * diagonal_scalar)
                    # Do not allow piece to move over the side of the board
                    if new_square in a_file or h_file:
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
        for vert_horiz_scalar in range(1, 7):
            for direction in (-8, -1, 1, 8):
                if 0 <= (self.square + direction * vert_horiz_scalar) <= 63:
                    all_moves.append(self.square + direction * vert_horiz_scalar)
                # Prevent useless calculations.
                else:
                    break
                    
        self.moves = sorted(all_moves)
    
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
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
        # Prevent going over side of board.
        # Switch these with board_obj attributes later on.
        a_file = [i * 8 for i in range(8)]
        h_file = [i * 8 + 7 for i in range(8)]
        # Vertical and horizontal moves
        for vert_horiz_scalar in range(1, 7):
            for direction in (-8, -1, 1, 8):
                if 0 <= (self.square + direction * vert_horiz_scalar) <= 63:
                    all_moves.append(self.square + direction * vert_horiz_scalar)
        # Diagonal moves
        for direction in (-9, -7, 7, 9):
            for diagonal_scalar in range(1, 7):
                new_square = self.square + direction * diagonal_scalar
                if 0 <= new_square <= 63:
                    all_moves.append(self.square + direction * diagonal_scalar)
                    # Do not allow piece to move over the side of the board
                    if new_square in a_file or h_file:
                        break
                # Prevent useless calculation.
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
        for delta in [7, 8, 9, -1, 1, -9, -8, -7]:
            if self.square + delta >= 0:
                all_moves.append(self.square + delta)         
        
        # TODO: Finish Castling - get rook to move as well
        if self.has_moved is False:
            if self.color == 'white':
                # Castle kingside
                if board.white_rk.has_moved is False \
                    and board.squares[5] == board.squares[6] == ' ':
                        all_moves.append(6)
                # Castle queenside
                if board.white_rq.has_moved is False \
                    and board.squares[1] == board.squares[2] == ' ':
                        all_moves.append(2)
            elif self.color == 'black':
                # Castle kingside
                if board.black_rk.has_moved is False \
                    and board.squares[61] == board.squares[62] == ' ':
                        all_moves.append(62)
                # Castle queenside
                if board.black_rq.has_moved is False \
                    and board.squares[57] == board.squares[58] == ' ':
                        all_moves.append(58)
                        
        # Remove illegal king moves into opponent controlled squares
        all_moves_set = set(all_moves)
        all_moves = list(all_moves_set)
        
        if self.color == 'white':
            for illegal_move in board.black_controlled_squares():
                try:
                    all_moves.remove(illegal_move)
                except ValueError:
                    pass
                
        elif self.color == 'black':
            for illegal_move in board.white_controlled_squares():
                try:
                    all_moves.remove(illegal_move)
                except ValueError:
                    pass
                
        self.moves = all_moves
    
    def move_piece(self, new_square: int):
        if new_square in self.moves:
            old_square = self.square
            self.square = new_square
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
    
    class TestPieceMovement(unittest.TestCase):
        def test_pawn(self):
            pawn = Pawn('Pa', 'white', 8)
            pawn.update_moves()
            self.assertEqual(pawn.moves, [16, 24])
            pawn.move_piece(24)
            self.assertEqual(pawn.square, 24)
            self.assertTrue(pawn.has_moved)
            pawn.update_moves()
            self.assertEqual(pawn.moves, [32])
            
            
            
    unittest.main()