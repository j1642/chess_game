"""Run this file to play chess.

Dependencies:
    board.py
    chess_utilities.py
    gui.py
    pieces.py
"""

import random
import sys
from time import gmtime, strftime
import traceback

import board
import chess_utilities
import engine
import gui
import pieces


class Game:
    """Controls the flow of the game.

    Methods
    -------
        __init__()
        __repr__()
        select_color()
        computer_turn()
        player_turn()
        is_valid_square()
        get_player_move_to()
        get_player_move_from()
        between_moves()
        play()

    """

    def __init__(self):
        self.player_color = ''
        self.computer_color = ''
        self.turn_color = 'white'
        self.white_wins = False
        self.black_wins = False
        self.board = board.Board()

        self.select_color()
        # Instantiating GUI before Game.select_color() opens blank window.
        self.display = gui.GUI()
        if self.player_color == 'white':
            self.display.perspective = 'white'
        else:
            self.display.perspective = 'black'

    def __repr__(self):
        return (f'Playing as {self.player_color}.\n'
                f'Turn: {self.turn_color}\n')

    def select_color(self):
        """Player chooses their piece color."""
        selected_color = input('Select your pieces: white, black, or '
                               'random?\n>>> ')
        if selected_color.lower() == 'random':
            selected_color = random.choice(['white', 'black'])
        if selected_color.lower() == 'white':
            self.player_color = 'white'
            self.computer_color = 'black'
            self.white_turn = self.player_turn
            self.black_turn = self.computer_turn
            self.player_king = self.board.white_king
        elif selected_color.lower() == 'black':
            self.player_color = 'black'
            self.computer_color = 'white'
            self.black_turn = self.player_turn
            self.white_turn = self.computer_turn
            self.player_king = self.board.black_king
        else:
            print('Invalid piece color.')
            return self.select_color()

    def computer_turn(self, move=None):
        """Make the computer's move. Currently, it plays a random move
        from all available moves.

        The `move` positional/keyword argument can force a specific move.
        `move` should be None or a tuple of squares to move from/to (ints
        or algebraic notation strings).
        """
        if self.computer_color == 'white':
            computer_pieces = self.board.white_pieces
        else:
            computer_pieces = self.board.black_pieces
        computer_moves = []
        for piece in computer_pieces:
            for computer_move in piece.moves:
                computer_moves.append(computer_move)
        computer_king = [piece for piece in computer_pieces
                         if isinstance(piece, pieces.King)][0]

        # TODO: DRY. Centralize computer and player checkmate/stalemate.
        if computer_moves == []:
            if computer_king.in_check:
                print('Player wins by checkmate! Thank you for playing!')
                return 'player wins by checkmate'
            else:
                print('Draw by stalemate! Thank you for playing!')
                return 'stalemate'

        if isinstance(move, tuple) and len(move) == 2 \
                and self.is_valid_square(move[0]) \
                and self.is_valid_square(move[1]) \
                and move[0] != move[1]:
            old_square = self.board.ALGEBRAIC_NOTATION.get(move[0], move[0])
            new_square = self.board.ALGEBRAIC_NOTATION.get(move[1], move[1])
            piece_to_move = self.board.squares[old_square]
            piece_to_move.move_piece(self.board, new_square)
        else:
            move_choices = []
            while move_choices == []:
                piece_to_move = random.choice(computer_pieces)
                move_choices = piece_to_move.moves
            assert move_choices
            assert piece_to_move

            old_square = piece_to_move.square
            new_square = random.choice(move_choices)
            piece_to_move.move_piece(self.board, new_square)
            assert old_square != piece_to_move.square

        self.turn_color = self.player_color

    def player_turn(self, old_square=None, move=None):
        """Human turn."""
        if self.player_color == 'white':
            player_pieces = self.board.white_pieces
        elif self.player_color == 'black':
            player_pieces = self.board.black_pieces
        player_moves = []
        for piece in player_pieces:
            for move in piece.moves:
                player_moves.append(move)
        # TODO: DRY. Centralize computer and player checkmate/stalemate.
        if player_moves == []:
            if self.player_king.in_check:
                print('Computer wins by checkmate! Thank you for playing!')
                return 'computer wins by checkmate'
            else:
                print('Draw by stalemate! Thank you for playing!')
                return 'stalemate'

        old_square, new_square = self.get_player_move()
        if new_square == -1:
            return self.player_turn()
        moving_piece = self.board.squares[old_square]
        result = moving_piece.move_piece(self.board, new_square)

        if isinstance(result, str):
            print('The selected piece cannot move there.')
            return self.player_turn()

        self.turn_color = self.computer_color

    def get_player_move(self):
        """Prompt for, validate, and return the squares to move from and to."""
        move = input('Squares to move from and to? (Ex: a1h8)\n')
        if len(move) != 4:
            print('Invalid move format.')
            return self.get_player_move()
        is_valid_move_from = self.is_valid_square(move[:2])
        is_valid_move_to = self.is_valid_square(move[2:])
        if not is_valid_move_from or not is_valid_move_to:
            print('Invalid move format.')
            return self.get_player_move()

        old_square = move[:2]
        if old_square.isdigit():
            old_square = int(old_square)
        else:
            old_square = self.board.ALGEBRAIC_NOTATION[old_square]
        try:
            if self.board.squares[old_square].color != self.player_color:
                print(f"One of your opponent's pieces is on {move[:2]}. "
                      'You cannot move that piece.')
                return self.get_player_move()
        except AttributeError:
            assert self.board.squares[old_square] == ' '
            print(f'There is no piece on {move[:2]}. Choose a square that'
                  ' has one of your pieces on it.')
            return self.get_player_move()

        new_square = move[2:]
        if new_square.isdigit():
            new_square = int(new_square)
        else:
            new_square = self.board.ALGEBRAIC_NOTATION[new_square]
        try:
            if self.board.squares[new_square].color == self.player_color:
                print(f'You cannot move to {new_square}. You already '
                      'have a piece there.')
                return self.get_player_move()
        except AttributeError:
            assert self.board.squares[new_square] == ' '
        return old_square, new_square

    def is_valid_square(self, user_input) -> bool:
        """Validate user move input."""
        if isinstance(user_input, int) or user_input.isdigit():
            square = int(user_input)
            if (0 <= square and square <= 63):
                return True
            return False
        elif user_input in self.board.ALGEBRAIC_NOTATION:
            return True
        print(f'{user_input} is not a valid algebraic notation square.')
        return False

    def between_moves(self):
        """All moves must be updated between turns so pieces know where
        they can go.
        """
        self.board.update_white_controlled_squares()
        self.board.update_black_controlled_squares()
        self.board.white_king.update_moves(self.board)

    # TODO: Entered infinite loop when checkmating as the black pieces.
    def play(self):
        """Play the game."""
        if not self.board.black_pieces + self.board.white_pieces:
            if self.computer_color == 'white':
                self.board.initialize_pieces(autopromote=['white'])
            else:
                self.board.initialize_pieces(autopromote=['black'])
        while True:
            self.display.update_gui(self.board)
            comp_move = None
            if self.computer_color == 'white':
                comp_move = engine.negamax(self.board, 2)[1]
            self.between_moves()
            self.board.remove_illegal_moves_for_pinned_pieces('white')
            res_white_turn = self.white_turn(move=comp_move)
            if res_white_turn:
                sys.exit(0)

            self.display.update_gui(self.board)
            comp_move = None
            if self.computer_color == 'black':
                comp_move = engine.negamax(self.board, 2)[1]
            self.between_moves()
            self.board.remove_illegal_moves_for_pinned_pieces('black')
            res_black_turn = self.black_turn(move=comp_move)
            if res_black_turn:
                sys.exit(0)


if __name__ == '__main__':

    def main():
        """Run the game."""
        game = Game()
        try:
            game.play()
        # Catch all exceptions. The except statement is intentionally vague.
        except Exception:
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
