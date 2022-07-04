import pieces


class Board:
    '''Holds the current board.'''
    
    def __init__(self):
        self.squares = [' '] * 64
        self.white_pieces = []
        self.black_pieces = []
        self.white_controlled_squares = []
        self.black_controlled_squares = []


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
            
        ls = '\n'.join(ranks_to_print)  # Looks nice w/ print( <board_object> )

        return ls


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

        for piece in self.white_pieces + self.black_pieces:
            self.squares[piece.square] = piece


    def update_moves_white(self):
        'Helper function for update_white_controlled_squares() method.'
        for piece in self.white_pieces:
            if isinstance(piece, pieces.King):
                piece.update_moves(self)
            else:
                piece.update_moves(self.squares)


    def update_moves_black(self):
        'Helper function for update_black_controlled_squares() method.'
        for piece in self.black_pieces:
            if isinstance(piece, pieces.King):
                piece.update_moves(self)
            else:
                piece.update_moves(self.squares)
                
                
    def update_king_moves(self):
        '''The king moves are dependant on the possbile move of all opponent
        pieces, so they must be updated last.
        '''
        for piece in board.white_pieces:
            if piece.name == 'K':
                white_king = piece
                break
        for piece in board.black_pieces:
            if piece.name == 'k':
                black_king = piece
                break
        
        white_king.check_if_in_check()
        black_king.check_if_in_check()
        
        white_king.update_moves()
        black_king.update_moves()
        

    def update_white_controlled_squares(self):
        '''Creates set to determine if black king is in check and limit 
        black king moves which would put it in check.'''
        white_controlled_squares = []

        self.update_moves_white()
        for piece in self.white_pieces:
            for move in piece.moves:
                white_controlled_squares.append(move)

        self.white_controlled_squares = set(white_controlled_squares)


    def update_black_controlled_squares(self):
        '''Creates set to determine if white king is in check and limit 
        white king moves which would put it in check.'''
        black_controlled_squares = []

        self.update_moves_black()        
        for piece in self.black_pieces:
            for move in piece.moves:
                black_controlled_squares.append(move)

        self.black_controlled_squares = set(black_controlled_squares)



if __name__ == '__main__':
    import unittest
    
    
    class test_board(unittest.TestCase):
        
        def test_repr_and_initialize_pieces(self):
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
            board = Board()
            board.initialize_pieces()
            board.update_white_controlled_squares()
            self.assertEqual(board.white_controlled_squares,
                             set(list(range(16, 32))))
        
        
        def test_update_black_controlled_squares(self):
            board = Board()
            board.initialize_pieces()
            board.update_black_controlled_squares()
            #print(board.white_pieces)
            self.assertEqual(board.black_controlled_squares,
                             set(list(range(32, 48))))
            
        
        def test_board_updates_upon_piece_movement(self):
            board = Board()
            board.initialize_pieces()
            
            # Test Pawn.move_piece() updates Board object.
            test_pawn = board.squares[8]
            test_pawn.update_moves(board.squares)
            board = test_pawn.move_piece(board, 16)
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
                if isinstance(piece, pieces.King):
                    piece.update_moves(board)
                else:
                    piece.update_moves(board.squares)
            
            # Test all piece types beside pawn, which was tested above.
            new_squares = (48, 18, 16, 0, 12, 23, 21, 1)
            for ind, piece in enumerate(board.squares[:8]):
                old_square = piece.square
                new_square = new_squares[ind]
                
                if isinstance(piece, pieces.King):
                    piece.update_moves(board)
                else:
                    piece.update_moves(board.squares)
                    
                board = piece.move_piece(board, new_square)

                if board.squares[old_square] == piece:
                    raise Exception(f'Invalid move for {piece.name}')
                
                self.assertEqual(board.squares[old_square], ' ')
                self.assertEqual(board.squares[new_square], piece)
                
                
        def test_capture_updates_board_and_piece_lists(self):
            board = Board()
            board.initialize_pieces()
            self.assertEqual(len(board.white_pieces), len(board.black_pieces))
            self.assertEqual(len(board.black_pieces), 16)
            
            # Scandinavian Defense captures
            board.update_white_controlled_squares()
            board.update_black_controlled_squares()
            board = board.squares[12].move_piece(board, 28)
            
            board.update_black_controlled_squares()
            board = board.squares[51].move_piece(board, 35)
            
            board.update_white_controlled_squares()
            board = board.squares[28].move_piece(board, 35)
            
            self.assertEqual(len(board.black_pieces), 15)
            for piece in board.black_pieces:
                self.assertTrue(piece.name != 'pd')
            
            board.update_black_controlled_squares()
            board = board.squares[59].move_piece(board, 35)
            
            self.assertEqual(len(board.white_pieces), 15)
            for piece in board.white_pieces:
                self.assertTrue(piece.name != 'Pe')
            
            
        def test_checked_king_moves_must_all_escape_check(self):
            '''Ensure that a checked king on e1 cannot move to f1 when an
            opponent's rook is checking the king from a1.
            
            This functionality requires the full Board class, not the limited
            Board class in the test section of pieces.py.
            
            This test is similar to one in pieces.py but this has a crucial
            addition at the end.
            '''
            board = Board()
            all_squares = board.squares
            king = pieces.King('K', 'white', 4)
            opponent_rook = pieces.Rook('ra', 'black', 0)
            self.assertFalse(king.in_check)
            
            all_squares[4] = king
            all_squares[0] = opponent_rook
            board.white_pieces.append(king)
            board.black_pieces.append(opponent_rook)
            
            king.update_moves(board)
            opponent_rook.update_moves(board.squares)
            
            king.remove_moves_to_attacked_squares(set(king.moves),
                                                  set(opponent_rook.moves))
            king.check_if_in_check(set(king.moves), set(opponent_rook.moves))
            self.assertTrue(king.in_check)
            
            king.update_moves(board)
            # This test was failing because board.black_pieces was empty.
            self.assertEqual(set(king.moves), set([11, 12 ,13]))
            
            
        def test_d2_pawn_can_move_to_27_and_update_board(self):
            board = Board()
            board.initialize_pieces()
            
        
        
        
        # TODO: game.py should check if the squares have changed and if so,
        # prompt same player for a valid move.
        
        
    unittest.main()
