'''
Run this file to play chess.

Dependencies (must be in same directory):
    board.py
    gui.py
    pieces.py
'''

from random import choice
import sys
from time import gmtime, strftime
import traceback

import board
import gui
import pieces


class Game:
    '''Controls player turns.'''
    #Should this stuff stay as a class or become the main program?
    def __init__(self):
        self.player_color = ''
        self.computer_color = ''
        self.turn_color = 'white'
        self.white_wins = False
        self.black_wins = False
        self.board = board.Board()

        self.board.initialize_pieces()
        self.select_color()

        self.display = gui.GUI()


    def __repr__(self):
        return f'''Playing as {self.player_color}.\nTurn: {self.turn_color}\n'''


    def select_color(self):
        '''Player chooses their piece color.'''
        # Delete this block when done testing and debuging.
        self.player_color, self.computer_color = 'white', 'black'
        self.white_turn, self.black_turn = self.player_turn, self.computer_turn
        self.player_moves = self.board.white_moves
        return

        selected_color = input('Pick your color: white or black?\n>>> ')
        if selected_color.lower() == 'white':
            self.player_color, self.computer_color = 'white', 'black'
            self.white_turn, self.black_turn = self.player_turn, self.computer_turn
            self.player_moves = self.board.white_moves
        elif selected_color.lower() == 'black':
            self.player_color, self.computer_color = 'black', 'white'
            self.black_turn, self.white_turn = self.player_turn, self.computer_turn
            self.player_moves = self.board.black_moves
        else:
            print('Input white or black.')


    def computer_turn(self):
        '''Computer turn. Currently, it plays a random move from all available
        moves.
        '''
        if self.computer_color == 'white':
            computer_pieces = self.board.white_pieces
            computer_moves = self.board.white_moves
        elif self.computer_color == 'black':
            computer_pieces = self.board.black_pieces
            computer_moves = self.board.black_moves
        else:
            raise Exception

        # Stalemate if computer has no possible moves to play.
        if computer_moves = []:
            print('Draw by stalemate. Game over.')
            sys.exit()

        move_choices = []
        while move_choices == []:
            piece_to_move = choice(computer_pieces)
            move_choices = piece_to_move.moves

        assert move_choices
        assert piece_to_move

        old_square = piece_to_move.square
        random_move = choice(move_choices)

        piece_to_move.move_piece(self.board, random_move)

        assert old_square != piece_to_move.square

        self.board.last_move_piece = piece_to_move
        self.board.last_move_from_to = (old_square, random_move)
        self.turn_color = self.player_color


    def player_turn(self, old_square=None):
        '''Human turn.'''
        print(self.board)
        # Check for stalemate.
        if self.player_moves = []:
            print('Draw by stalemate. Game over.')
            sys.exit()

        print(f'\n{self.player_color.capitalize()} to move.')

        try:
            old_square = int(input('Square to move from? (int)\n>>> '))
        except TypeError:
            print('Square to move from must be an int where you have a piece.')
            old_square = int(input('Square to move from? (int)\n>>> '))

        try:
            if self.board.squares[old_square].color != self.player_color:
                print(f"One of your opponent's pieces is on square {old_square}.")
                self.player_turn()
        except AttributeError:
            assert self.board.squares[old_square] == ' '
            print('There is no piece on that square. Choose a square that has',
                  'one of your pieces on it.')
            self.player_turn()

        new_square = int(input('Square to move to? (int)\n>>> '))

        moving_piece = self.board.squares[old_square]
        if isinstance(moving_piece, pieces.King):
            result = moving_piece.move_piece(self.board, new_square)
        else:
            result = moving_piece.move_piece(self.board, new_square)

        if isinstance(result, str):
            print('The selected piece cannot move there. Input a valid square',
                  'for the selected piece to move to. (int)')
            new_square = input('>>> ')
            self.player_turn()

        self.board.last_move_piece = moving_piece
        self.board.last_move_from_to = (old_square, new_square)
        self.turn_color = self.computer_color


    def between_moves(self):
        '''All moves must be updated between turns so pieces know where they
        can go.
        '''
        self.board.update_white_controlled_squares()
        self.board.update_black_controlled_squares()

        # Update king moves again now that all other piece moves are known.
        # Needed to determine if in check and to remove illegal king moves.
        self.board.white_king.update_moves(self.board)
        self.board.black_king.update_moves(self.board)

        # TODO: self.check_for_stalemate(self.board)
        #
        # check if a piece is pinned to the king before moving it:
        #   - Update a dummy board and check if friendly king is in check.


        # TODO: choose terminal or GUI


    def play(self):
        '''Play chess.'''
        checkmate = False
        while not checkmate:
            self.between_moves()
            if checkmate:
                print('Checkmate after game.black_turn()')
                break
            self.display.update_gui(self.board)
            self.white_turn()
            self.between_moves()
            if checkmate:
                print('Checkmate after game.white_turn()')
                break
            self.display.update_gui(self.board)
            self.black_turn()



if __name__ == '__main__':

    def main():
        game = Game()
        try:
            game.play()
        except Exception:
            e_type, e_val, e_tb = sys.exc_info()
            traceback.print_exception(e_type, e_val, e_tb)
            # Add error to bug tracking log
            current_time = strftime('%Y-%m-%d %H:%M', gmtime())
            with open('chess_bug_log.txt', 'a') as log:
                log.write(f'{current_time}\n')
                traceback.print_exception(e_type, e_val, e_tb, file=log)
                log.write('\n\n')

            # save current board config
            # upon start, ask player if they want to load game

    main()
