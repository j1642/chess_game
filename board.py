from os import chdir, getcwd
if getcwd().split('/')[-1] != 'chess':
    chdir('Python/chess')

import pieces

class Board:
    '''Holds the current board.'''
    
    def __init__(self):
        self.squares = [' '] * 64
        self.squares_occ_white = []
        self.squares_occ_black = []
        self.white_pieces = []
        self.black_pieces = []


    def __repr__(self):
        '''Shows the current board. Useful for feedback to user before GUI
        is implememnted. Starts from the eighth rank (row).'''
        
        ranks_to_print = []
        for factor in range(7, -1, -1):
            rank_x = ['|']
            for square in range(factor * 8, factor * 8 + 8):
                rank_x.append(self.squares[square])
                rank_x.append('|')
            ranks_to_print.append(''.join(rank_x))
        ls = '\n'.join(ranks_to_print)  # Looks nice w/ print( <board_object> )

        return ls


    def set_initial_squares(self):
        '''Sets up the board for a new game.'''

        ranks1_2 = ['R','N', 'B', 'Q', 'K', 'B', 'N', 'R', 'P', 'P', 'P',
                  'P', 'P', 'P', 'P', 'P']

        for i in range(16):
            self.squares[i] = ranks1_2[i]
        ranks1_2.reverse()
        for i in range(48, 64):
            self.squares[i] = ranks1_2[(i - 48)].lower()
        # Manually change black king and queen positions b/c they are mirrored
        self.squares[60] = 'k'
        self.squares[59] = 'q'


    # TODO: Compare move list for all pieces to the occupied lists to cut
    #   illegal moves.
    def find_occupied_squares(self):
        '''Gets lists of squares occupied by white and black pieces,
        respectively.

        These lists are used to prevent a white piece moving to a square
        occupied by another white piece, for example.'''
        self.squares_occ_white = []
        self.squares_occ_black = []
        
        for ind, square in enumerate(self.squares):
            if square.isupper():
                self.squares_occ_white.append(ind)
            elif square.islower():
                self.squares_occ_black.append(ind)


    # Variable suffix corresponds to starting file (column) of a piece.
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


    def update_moves_white(self, white_pieces: list):
        'Helper function for update_white_controlled_squares() method.'
        for piece in white_pieces:
            piece.update_moves()


    def update_moves_black(self, black_pieces: list):
        'Helper function for update_black_controlled_squares() method.'
        for piece in black_pieces:
            piece.update_moves()


    def update_white_controlled_squares(self, white_pieces: list):
        '''Creates set to determine if black king is in check and limit 
        black king moves which would put it in check.'''
        white_controlled_squares = []

        self.update_moves_white(self.white_pieces)
        for piece in white_pieces:
            for move in piece.moves:
                white_controlled_squares.append(move)

        self.white_controlled_squares = set(white_controlled_squares)


    def update_black_controlled_squares(self, black_pieces: list):
        '''Creates set to determine if white king is in check and limit 
        white king moves which would put it in check.'''
        black_controlled_squares = []

        self.update_moves_black(self.black_pieces)        
        for piece in black_pieces:
            for move in piece.moves:
                black_controlled_squares.append(move)

        self.black_controlled_squares = set(black_controlled_squares)



if __name__ == '__main__':
    import unittest
    
    
    class test_board(unittest.TestCase):
        
        def test_set_initial_squares(self):
            board = Board()
            self.assertEqual(board.squares, [' '] * 64)
            
            board.set_initial_squares()
            self.assertEqual(board.squares, ['R','N', 'B', 'Q', 'K', 'B', 'N',
                                             'R', 'P', 'P', 'P', 'P', 'P', 'P',
                                             'P', 'P']
                                             + [' '] * 32
                                             + ['p', 'p', 'p', 'p', 'p', 'p',
                                                'p', 'p', 'r', 'n', 'b', 'q',
                                                'k', 'b', 'n', 'r'])
        
        
        def test_repr(self):
            board = Board()
            board.set_initial_squares()
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
        
            
        def test_find_occupied_squares(self):
            board = Board()
            
            board.set_initial_squares()
            self.assertEqual(board.squares_occ_white, board.squares_occ_black)
            self.assertEqual(board.squares_occ_black, [])
            
            board.find_occupied_squares()
            self.assertEqual(board.squares_occ_white, list(range(16)))
            self.assertEqual(board.squares_occ_black, list(range(48, 64)))
            
            board.squares[0], board.squares[27] = board.squares[27], \
                                                  board.squares[0]
            board.find_occupied_squares()
            self.assertEqual(board.squares_occ_white, list(range(1,16)) + [27])
        
        
        def test_initialize_pieces(self):
            # This is not particularly thorough, however there is not much
            #     to test for this method.
            board = Board()
            self.assertEqual(board.white_pieces, board.black_pieces)
            board.initialize_pieces()
            self.assertEqual(len(board.white_pieces), len(board.black_pieces))
            self.assertEqual(len(board.black_pieces), 16)
            print(board.black_pieces)
        
        
        def update_moves_white(self):
            pass
        
        
        def update_moves_black(self):
            pass
        
        
        def update_white_controlled_squares(self):
            pass
        
        
        def update_black_controlled_squares(self):
            pass
        
        
    unittest.main()
