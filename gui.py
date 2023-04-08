"""Provide a graphical display, in addition to the ASCII standard
outputs to the terminal.
"""
import sys
import tkinter as tk


class GUI:
    """Visual representation of a chessboard.

    Methods
    -------
        __init__()
        find_dark_light_squares()
        empty_function()
        update_gui()
        find_command_make_button()

    """

    def __init__(self):
        # Disable display in CI/CD to avoid TclError
        if sys.version[:6] == '3.10.8' and sys.platform == 'linux':
            print('Remove the gui.__init__() check if you are using '
                  'Python 3.10.8 on Linux.')
            return

        self.dark_squares, self.light_squares = self.find_dark_light_squares()
        self.image_references = [0] * 64
        self.buttons = [0] * 64
        self.root = tk.Tk()
        self.root.geometry('400x405+380+430')
        self.root.title('Chess')
        self.perspective = None

    def find_dark_light_squares(self) -> tuple:
        """Return sets of which chessboard squares are dark and which are
        light.
        """
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
        """Use as the command keyword argument for the empty square
        buttons.
        """
        pass

    def update_gui(self, chessboard, selected_piece=None):
        """Update the GUI based on current state of chessboard.squares."""
        files = 'abcdefgh'
        ranks = range(8, 0, -1)
        if self.perspective == 'black':
            files = reversed(files)
            ranks = range(1, 9)
        # Add rank and file labels
        for ind, char in enumerate(files):
            label = tk.Label(self.root,
                             text=char,
                             font=('Helvetica', 11)
                             )
            label.grid(column=ind + 1, row=8)
        for ind, num in enumerate(ranks):
            label = tk.Label(self.root,
                             text=str(num),
                             font=('Helvetica', 11)
                             )
            label.grid(column=0, row=ind)

        squares = chessboard.squares
        if self.perspective == 'black':
            squares = reversed(chessboard.squares)
        for ind, square in enumerate(squares):
            IS_DARK_SQUARE = ind in self.dark_squares
            # Column plus 1 makes space for row labels in column 0
            # Row number calculations give a minimum result of 1, not 0.
            row_num = abs(ind // 8 - 8) - 1
            column_num = ind % 8 + 1
            if square == ' ':
                if IS_DARK_SQUARE:
                    image_path = 'assets/dark_square.png'
                else:
                    image_path = 'assets/light_square.png'
            elif square.color == 'white' or square.color == 'black':
                color = square.color
                piece_type = str(type(square)).split('.')[1].split("\'")[0]\
                    .lower()

                image_path = ''.join(['assets/', color, '_', piece_type])

                if IS_DARK_SQUARE:
                    image_path = ''.join([image_path, '_on_dark.png'])
                else:
                    image_path = ''.join([image_path, '_on_light.png'])
            else:
                raise Exception(f'Square {ind}: contents invalid.')

            image_path = tk.PhotoImage(file=image_path)
            # Need to store PhotoImage object reference to display it
            # after the for loop and function end.
            self.image_references[ind] = image_path

            self.find_command_make_button(chessboard,
                                          (image_path, column_num,
                                              row_num, ind, square),
                                          selected_piece)
        # update_idletasks() disables GUI click interaction.
        self.root.update_idletasks()

    def find_command_make_button(self, chessboard,
                                 image_column_row_index_square: tuple,
                                 selected_piece):
        """Make buttons and adds them to the grid.

        Having this method removes bug where all buttons with pieces on
        them refer to the black h rook, due to the final value of ind from
        enumerate() being 63.
        """
        image, column, row, index, square = image_column_row_index_square

        if selected_piece is None:
            all_squares = chessboard.squares
            command = lambda: self.update_gui(
                chessboard, selected_piece=all_squares[index])
            if square == ' ':
                command = lambda: self.empty_function()
        else:
            command = lambda: selected_piece.move_piece(chessboard, index)

        if self.buttons[index] == 0:
            button = tk.Button(
                self.root,
                image=image,
                highlightthickness=0,
                bd=0,
                borderwidth=0,
                padx=0,
                pady=0,
                # Commands not currently supported.
                command=self.empty_function())
            self.buttons[index] = button
        else:
            self.buttons[index]['image'] = image
        self.buttons[index].grid(column=column, row=row, padx=0, pady=0,
                                 ipadx=0, ipady=0)
