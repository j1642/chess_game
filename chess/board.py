import pieces

class Board:
    '''Holds current board'''
    def __init__(self):
        self.squares = [' '] * 64
        self.squares_occ_white = []
        self.squares_occ_black = []
        self.white_pieces_ls = []
        self.black_pieces_ls = []
        
        self.a_file = [i * 8 for i in range(8)]
        self.b_file = [i * 8 + 1 for i in range(8)]
        self.c_file = [i * 8 + 2 for i in range(8)]
        self.d_file = [i * 8 + 3 for i in range(8)]
        self.e_file = [i * 8 + 4 for i in range(8)]
        self.f_file = [i * 8 + 5 for i in range(8)]
        self.g_file = [i * 8 + 6 for i in range(8)]
        self.h_file = [i * 8 + 7 for i in range(8)]

        self.rank_1 = [i for i in range(8)]
        self.rank_2 = [i for i in range(8, 16)]
        self.rank_3 = [i for i in range(16, 24)]
        self.rank_4 = [i for i in range(24, 32)]
        self.rank_5 = [i for i in range(32, 40)]
        self.rank_6 = [i for i in range(40, 48)]
        self.rank_7 = [i for i in range(48, 56)]
        self.rank_8 = [i for i in range(56, 64)]
    
    def __repr__(self):
        '''Shows the current board. Useful for feedback to user before GUI.'''
        
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
    
    # TODO: Does not work
    # TODO: Compare move list for all pieces to the occupied lists to cull illegal moves
    def find_occupied_squares(self):
        '''Gets lists of squares occupited by white and black pieces, respectively.
        
        These lists are used to prevent a white piece moving to a square occupied 
        by another white piece, for example.'''
        
        for square in self.squares:
            if square.isupper():
                self.squares_occ_white.append(self.squares.index(square))
                #print(self.squares.index(square))
            elif square.islower():
                self.squares_occ_black.append(self.squares.index(square))

    # Can these variable names be improved?
    def initialize_pieces(self):
        white_rq = pieces.Rook('rook queenside', 'white', 0)
        white_nq = pieces.Knight('knight queenside', 'white', 1)
        white_bq = pieces.Bishop('bishop queenside', 'white', 2)
        white_q = pieces.Queen('Queen', 'white', 3)
        white_k = pieces.King('King', 'white', 4)
        white_bk = pieces.Bishop('bishop kingside', 'white', 5)
        white_nk = pieces.Knight('knight kingside', 'white', 6)
        white_rk = pieces.Rook('rook kingside', 'white', 7)
        
        white_pa = pieces.Pawn('pawn a', 'white', 8)
        white_pb = pieces.Pawn('pawn b', 'white', 9)
        white_pc = pieces.Pawn('pawn c', 'white', 10)
        white_pd = pieces.Pawn('pawn d', 'white', 11)
        white_pe = pieces.Pawn('pawn e', 'white', 12)
        white_pf = pieces.Pawn('pawn f', 'white', 13)
        white_pg = pieces.Pawn('pawn g', 'white', 14)
        white_ph = pieces.Pawn('pawn h', 'white', 15)
        
        self.white_pieces_ls.append(white_rq, white_nq, white_bq, white_q, \
                                    white_k, white_bk, white_nk, white_rk, \
                                    white_pa, white_pb, white_pc, white_pd, \
                                    white_pe, white_pf, white_pg, white_ph)
        
        black_rq = pieces.Rook('rook queenside', 'black', 56)
        black_nq = pieces.Knight('knight queenside', 'black', 57)
        black_bq = pieces.Bishop('bishop queenside', 'black', 58)
        black_q = pieces.Queen('queen', 'black', 59)
        black_k = pieces.King('king', 'black', 60)
        black_bk = pieces.Bishop('bishop kingside', 'black', 61)
        black_nk = pieces.Knight('knight kingside', 'black', 62)
        black_rk = pieces.Rook('rook kingside', 'black', 63)
        
        black_pa = pieces.Pawn('pawn a', 'black', 48)
        black_pb = pieces.Pawn('pawn b', 'black', 49)
        black_pc = pieces.Pawn('pawn c', 'black', 50)
        black_pd = pieces.Pawn('pawn d', 'black', 51)
        black_pe = pieces.Pawn('pawn e', 'black', 52)
        black_pf = pieces.Pawn('pawn f', 'black', 53)
        black_pg = pieces.Pawn('pawn g', 'black', 54)
        black_ph = pieces.Pawn('pawn h', 'black', 55)
        
        self.black_pieces_ls.append(black_rq, black_nq, black_bq, black_q, \
                                    black_k, black_bk, black_nk, black_rk, \
                                    black_pa, black_pb, black_pc, black_pd, \
                                    black_pe, black_pf, black_pg, black_ph)
            
    def get_updated_moves_white(self, white_pieces_ls: list):
        for piece in white_pieces_ls:
            piece.update_moves()
            
    def get_updated_moves_black(self, black_pieces_ls: list):
        for piece in black_pieces_ls:
            piece.update_moves()
    
    def white_controlled_squares(self, white_pieces_ls: list):
        '''Creates set to determine if black king is in check and limit 
        black king moves which would put it in check.'''
        # Could use sets but list.append() is O(1)
        white_controlled_squares = []
        
        self.get_updated_moves_white(self.white_pieces_ls)
        for piece in white_pieces_ls:
            for move in piece.moves:
                white_controlled_squares.append(move)

        return sorted(set(white_controlled_squares))
                
    def black_controlled_squares(self, black_pieces_ls: list):
        '''Creates set to determine if white king is in check and limit 
        white king moves which would put it in check.'''
        # Could use sets but list.append() is O(1)
        black_controlled_squares = []
        
        self.get_updated_moves_black(self.black_pieces_ls)        
        for piece in black_pieces_ls:
            for move in piece.moves:
                black_controlled_squares.append(move)
                
        return sorted(set(black_controlled_squares))
                
b = Board()
b.set_initial_squares()
print(b)