'''
This module provides an alternative to playing chess in the terminal with
ASCII graphics.
'''
import tkinter as tk



class GUI:
    def __init__(self, chessboard):
        self.dark_squares, self.light_squares = self.find_dark_light_squares()
        self.image_references = [0] * 64

        self.root = tk.Tk()
        self.root.geometry('380x380+480+400')
        self.root.title('Chess')

        self.update_gui(chessboard)
        self.root.mainloop()






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


    def update_gui(self, chessboard, selected_piece=None):
        '''Update the GUI based on current state of chessboard.squares.'''

        for ind, square in enumerate(chessboard.squares):
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
            # Need to store Photoimage object reference to display it after the
            # for loop and function end.
            self.image_references[ind] = image_path

            self.find_command_make_button(chessboard,
                                          (image_path, column_num, row_num, ind, square),
                                          selected_piece)


    def find_command_make_button(self, chessboard,
                                 image_column_row_index_square: tuple,
                                 selected_piece):
        '''Makes buttons and adds them to the grid.

        Helper method for update_gui().

        Having this method removes bug where all buttons with pieces on them
        refer to the black h rook, due to the final value of ind from
        enumerate() being 63.
        '''
        image, column, row, index, square = image_column_row_index_square

        if selected_piece is None:
            all_squares = chessboard.squares
            command = lambda : self.update_gui(chessboard, selected_piece=all_squares[index])
            if square == ' ':
                command = lambda : self.empty_function()
        else:
            command = lambda : selected_piece.move_piece(chessboard, index)

        button = tk.Button(
            self.root,
            image=image,
            highlightthickness=0,
            bd=0,
            borderwidth=0,
            command=command
            )

        button.grid(column=column, row=row)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('380x380+500+500')
    root.title('Chess')

    gui = GUI()
    root.mainloop()
