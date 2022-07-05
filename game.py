import board
import pieces

import sys
import traceback
from random import choice
from time import gmtime, strftime


class Game:
    '''Controls player turns.'''
    #Should this stuff stay as a class or become the main program?
    def __init__(self):
        self.player_color = ''
        self.computer_color = ''
        self.turn_color = 'white'
        self.last_move_piece = None
        self.last_move_square = None
        self.board = board.Board()
        
        self.board.initialize_pieces()
        self.white_king = [i for i in self.board.white_pieces if isinstance(i, pieces.King)][0]
        self.black_king = [i for i in self.board.black_pieces if isinstance(i, pieces.King)][0]
        
        
        self.select_color()
        

    def __repr__(self):
        return f'''Playing as {self.player_color}.\nTurn: {self.turn}\n'''
        
    
    def white_turn(self):
        pass
    
    
    def black_turn(self):
        pass
    

    def select_color(self):
        selected_color = input('Pick your color: white or black?\n>>> ')
        if selected_color.lower() == 'white':
            self.player_color, self.computer_color = 'white', 'black'
            self.white_turn, self.black_turn = self.player_turn, self.computer_turn
        elif selected_color.lower() == 'black':
            self.player_color, self.computer_color = 'black', 'white'
            self.black_turn, self.white_turn = self.player_turn, self.computer_turn
        else:
            print('Input white or black.')
            
            
    def computer_turn(self):
        if self.computer_color == 'white':
            computer_pieces = self.board.white_pieces
        elif self.computer_color == 'black':
            computer_pieces = self.board.black_pieces
        else:
            raise Exception
        
        move_choices = []
        while move_choices == []:
            piece_to_move = choice(computer_pieces)
            move_choices = piece_to_move.moves
            
        assert move_choices
        assert piece_to_move
        
        random_move = choice(move_choices)
        
        piece_to_move.move_piece(self.board, random_move)
        
        self.turn_color = self.player_color
            
    
    def player_turn(self, old_square=None):
        print(self.board)
        print(f'\n{self.player_color.capitalize()} to move.')
        
        try:
            old_square = int(input('Square to move from? (int)\n>>> '))
        except TypeError:
            print('Square to move from must be an int where you have a piece.')
            old_square = int(input('Square to move from? (int)\n>>> '))
        
        try:
            if self.board.squares[old_square].color != self.player_color:
                print(f"One of your opponent's pieces is on square {old_square}.")
                self.black_to_move()
        except AttributeError:
            assert self.board.squares[old_square] == ' '
            print('There is no piece on that square. Choose a square that has',
                  'one of your pieces on it.')
            self.black_to_move()
            
        new_square = int(input('Square to move to? (int)\n>>> '))
            
        moving_piece = self.board.squares[old_square]
        if isinstance(moving_piece, pieces.King):
            result = moving_piece.move_piece(self.board, new_square)
        else:
            result = moving_piece.move_piece(self.board, new_square)
            
        if isinstance(result, str) and result.split(' ')[0] == 'Not':
            print('The selected piece cannot move there. Input a valid square',
                  'for the selected piece to move to. (int)')
            new_square = input('>>> ')
            self.black_to_move(old_square, new_square)

        self.last_move_piece = type(moving_piece)
        self.last_move_square = new_square
        # TODO: make en-passant available to adjacent pawns
        
        self.turn_color = self.computer_color
            
    
    def between_moves(self):
        white_controlled_squares = self.board.white_controlled_squares
        black_controlled_squares = self.board.black_controlled_squares
        
        self.board.update_white_controlled_squares()
        self.board.update_black_controlled_squares()
        
        self.white_king.remove_moves_to_attacked_squares(white_controlled_squares,
                                                         black_controlled_squares)
        self.black_king.remove_moves_to_attacked_squares(white_controlled_squares,
                                                         black_controlled_squares)
        
        self.white_king.check_if_in_check(white_controlled_squares,
                                          black_controlled_squares)
        self.black_king.check_if_in_check(white_controlled_squares,
                                          black_controlled_squares)
        
            
    def play(self):
        checkmate = False
        while not checkmate:
            self.between_moves()
            self.white_turn()
            self.between_moves()
            self.black_turn()
        
        
        
if __name__ == '__main__':
    
    game = Game()
    try:
        game.play()
    except Exception as e:
        e_type, e_val, e_tb = sys.exc_info()
        traceback.print_exception(e_type, e_val, e_tb)
        # add error to bug tracking log
        current_time = strftime('%Y-%m-%d %H:%M', gmtime())
        with open('bug_log.txt', 'a') as f:
            f.write(f'{current_time}\n')
            traceback.print_exception(e_type, e_val, e_tb, file=f)
            f.write('\n\n')
        
        # save current board config
        # upon start, ask player if they want to load game
    