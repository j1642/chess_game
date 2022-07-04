import board
import pieces


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
        
        self.between_moves()


    def __repr__(self):
        return f'''Playing as {self.player_color}.\nTurn: {self.turn}\n'''
        

    def select_color(self):
        print('This version is a two-player game with both players using the',
              'same computer.')
        selected_color = input('Pick your color: white or black?\n>>> ')
        if selected_color.lower() == 'white':
            self.player_color, self.comupter_color = 'white', 'black'
        elif selected_color.lower() == 'black':
            self.player_color, self.comupter_color = 'black', 'white'
        else:
            print('Input white or black.')
            
    
    def turn(self, turn_color: str, old_square=None):
        print(self.board)
        print(f'\n{turn_color.capitalize()} to move.')
        
        try:
            old_square = int(input('Square to move from? (int)\n>>> '))
        except TypeError:
            print('Square to move from must be an int where you have a piece.')
            old_square = int(input('Square to move from? (int)\n>>> '))
        
        try:
            if self.board.squares[old_square].color != turn_color:
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
        else:
            self.board = result
        
        self.last_move_piece = type(moving_piece)
        self.last_move_square = new_square
        # TODO: make en-passant available to adjacent pawns
        
        if turn_color == 'white':
            self.turn_color = 'black'
        elif turn_color == 'black':
            self.turn_color = 'white'
            
        self.between_moves()
    
    
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
        
        if self.turn_color == 'white':
            self.turn('white')
        elif self.turn_color == 'black':
            self.turn('black')
        
        
if __name__ == '__main__':
    
    Game()
    