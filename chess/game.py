import board

class Game:
    '''Should this stuff stay as a class or become the main program?'''
    def __init__(self):
        self.player_color = ''
        self.computer_color = ''
        self.turn = ''
        
        Game.select_color(self)
        
        # May Use elif, not else, to help avoid weird inputs
        if self.player_color == 'white':
            self.turn = 'player'
        elif self.computer_color == 'white':
            self.turn = 'computer'
            
    def __repr__(self):
        return f'''Playing as {self.player_color}.\nTurn: {self.turn}\nThere are
        {len(self.pieces_on_board)} pieces on the board.'''
        
    # TODO: Test what happens if there is a weird input
    def select_color(self):
        selected_color = input('Pick your color: white or black?\n')
        if selected_color.lower() == 'white':
            self.player_color, self.comupter_color = 'white', 'black'
        elif selected_color.lower() == 'black':
            self.player_color, self.comupter_color = 'black', 'white'
        else:
            return 'Input <white> or <black>.'
    
    # TODO
    # Algorithms for the computer to make a move
    def computer_move():
        pass
        # .....
        self.turn = 'player'
        self.between_moves()
    
    # TODO
    def player_move():
        old_square = input('Square to move from? (int)')
        new_square = input('Square to move to? (int)')
        symbol = board.squares[old_square]
        
        self.turn = 'computer'
        self.between_moves()
        
    # TODO
    def between_moves():
        self.in_check()
        #update_moves for all pieces in pieces_on_board
    
    # TODO: finish
    def in_check(self):
        # if square[king_black] in [white_controlled_squares]:
            # 
    
    