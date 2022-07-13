'''
This module provides an alternative to playing chess in the terminal with
ASCII graphics.
'''
import tkinter as tk

import board
import pieces


class GUI:
    def __init__(self):
        self.chessboard = board.Board()
        self.image_references = [0] * 64

        self.dark_squares, self.light_squares = self.find_dark_light_squares()

        self.chessboard.initialize_pieces()

        self.update_gui(self.chessboard)


    def find_dark_light_squares(self) -> tuple:
        '''Return sets of which chessboard squares are dark and which are
        light.
        '''
        dark_squares = []
        light_squares = []
        for square in range(64):
            row = square // 8
            column = square % 8
            if row % 2 == 0:
                if column % 2 == 0:
                    dark_squares.append(square)
                else:
                    light_squares.append(square)
            else:
                if column % 2 == 0:
                    light_squares.append(square)
                else:
                    dark_squares.append(square)

        assert set(range(64)) == set(light_squares + dark_squares)

        return set(dark_squares), set(light_squares)


    def empty_function(self):
        '''Used as the command keyword argument for the empty square buttons.
        '''
        pass


    def return_piece(self, square):
        return square


    def update_gui(self, selected_piece=None):
        '''Update the GUI based on current state of chessboard.squares.'''
        # Need to store Photoimage object reference to display it after the for
        # loop and function end.
        for ind, square in enumerate(self.chessboard.squares):
            IS_DARK_SQUARE = ind in self.dark_squares
            row_num = abs(ind // 8 - 8)
            column_num = ind % 8
            if square == ' ':
                if IS_DARK_SQUARE:
                    image_path = 'assets/dark_square.png'
                else:
                    image_path = 'assets/light_square.png'
            elif square.color == 'white' or square.color == 'black':
                color = square.color
                piece_type = str(type(square)).split('.')[1]\
                            .split("\'")[0].lower()

                image_path = ''.join(['assets/', color, '_', piece_type])

                if IS_DARK_SQUARE:
                    image_path = ''.join([image_path, '_on_dark.png'])
                else:
                    image_path = ''.join([image_path, '_on_light.png'])
            else:
                raise Exception(f'Square {ind}: contents invalid.')

            image_path = tk.PhotoImage(file=image_path)
            self.image_references[ind] = image_path

            # TODO: attribute error b/c selected_piece type is Board?
            #print(type(self.chessboard.squares[ind]))
            if selected_piece is None:
                all_squares = self.chessboard.squares
                command = lambda : self.update_gui(selected_piece=all_squares[ind])
                if square == ' ':
                    command = lambda : self.empty_function()
            else:
                command = lambda : selected_piece.move_piece(ind, self.chessboard)


            button = tk.Button(
                root,
                image=image_path,
                highlightthickness=0,
                bd=0,
                borderwidth=0,
                command=command
                )

            button.grid(column=column_num, row=row_num)


root = tk.Tk()
root.geometry('380x380+400+300')
root.title('Chess')

gui = GUI()
root.mainloop()
