"""Run this file to play chess.

Dependencies (must be in same directory):
    board.py
    chess_utilities.py
    gui.py
    pieces.py
"""

from random import choice
import sys
from time import gmtime, strftime
import traceback

import board
import chess_utilities
import gui
import pieces


class Game:
    """Controls player turns."""

    # Should this stuff stay as a class or become the main program?
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
        return (f'Playing as {self.player_color}.\n'
                f'Turn: {self.turn_color}\n')

    def select_color(self):
        """Player chooses their piece color."""
        # TODO: Delete this block when done testing and debuging.
        self.player_color, self.computer_color = 'white', 'black'
        self.white_turn, self.black_turn = self.player_turn, self.computer_turn
        self.player_moves = self.board.white_moves
        self.player_king = self.board.white_king
        return

        selected_color = input('Pick your color: white or black?\n>>> ')
        if selected_color.lower() == 'white':
            self.player_color, self.computer_color = 'white', 'black'
            self.white_turn, self.black_turn = self.player_turn, \
                self.computer_turn
            self.player_moves = self.board.white_moves
            self.player_king = self.board.white_king
        elif selected_color.lower() == 'black':
            self.player_color, self.computer_color = 'black', 'white'
            self.black_turn, self.white_turn = self.player_turn, \
                self.computer_turn
            self.player_moves = self.board.black_moves
            self.player_king = self.board.black_king
        else:
            print('Input white or black.')

    def computer_turn(self):
        """Make the computer's move. Currently, it plays a random move
        from all available moves.
        """
        if self.computer_color == 'white':
            computer_pieces = self.board.white_pieces
            computer_moves = self.board.white_moves
        elif self.computer_color == 'black':
            computer_pieces = self.board.black_pieces
            computer_moves = self.board.black_moves
        else:
            raise Exception
        computer_king = [piece for piece in computer_pieces
                         if isinstance(piece, pieces.King)]

        # TODO: Completed stalemate, incomplete checkmate.
        if computer_moves == []:
            if computer_king.in_check:
                print('Player wins by checkmate. Game over.')
            else:
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
        """Human turn."""
        print(self.board)
        if self.player_color == 'white':
            self.player_moves = self.board.white_moves
        elif self.player_color == 'black':
            self.player_moves = self.board.black_moves
        # TODO: Completed stalemate, incomplete checkmate.
        if self.player_moves == []:
            if self.player_king.in_check:
                print('Computer wins by checkmate. Game over.')
            else:
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
                print(f"One of your opponent's pieces is on square "
                      f'{old_square}.')
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
        """All moves must be updated between turns so pieces know where
        they can go.
        """
        self.board.update_white_controlled_squares()
        self.board.update_black_controlled_squares()

        # Update king moves again now that all other piece moves are known
        self.board.white_king.update_moves(self.board)
        # Black king should not have to update again b/c
        # white_controlled_squares were known prior to the black king
        # updating its moves.
        # self.board.black_king.update_moves(self.board)

        # TODO: check if a piece is pinned to the king before moving it:
        #   - by Updating dummy board and check if friendly king is in check.

        # TODO: choose terminal or GUI

    def play(self):
        """Play the game. The while loop ends by sys.exit() in
        Game.player_turn() or Game.computer_turn().
        """
        while True:
            self.between_moves()
            self.display.update_gui(self.board)
            self.white_turn()
            self.between_moves()
            self.display.update_gui(self.board)
            self.black_turn()


if __name__ == '__main__':

    def main():
        """Run the game."""
        game = Game()
        try:
            game.play()
        # Catch all exceptions. The except statement is intentionally vague.
        except Exception:
            # Next two lines from Stack Overflow.
            e_type, e_val, e_tb = sys.exc_info()
            traceback.print_exception(e_type, e_val, e_tb)
            # Store chessboard in database for debugging.
            db_e_type = str(e_type).split("'")[1]
            db_e_val = str(e_val)
            chess_utilities.pickle_and_add_board_to_db(game.board, db_e_type,
                                                       db_e_val)
            # Add error to bug tracking log
            current_time = strftime('%Y-%m-%d %H:%M', gmtime())
            with open('chess_bug_log.txt', 'a') as log:
                log.write(f'{current_time}\n')
                traceback.print_exception(e_type, e_val, e_tb, file=log)
                log.write('\n')
                log.write(chess_utilities.export_board_to_fen(game.board))
                log.write('\n\n')
            # Next steps: upon start, ask player if they want to load game

    main()
