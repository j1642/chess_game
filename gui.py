import tkinter as tk
#from tkinter import ttk
import board
import pieces

chessboard = board.Board()
chessboard.initialize_pieces()


def find_dark_light_squares() -> tuple:
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



dark_squares, light_squares = find_dark_light_squares()

root = tk.Tk()
root.geometry('380x380+400+300')
root.title('Chess')

# Need to store Photoimage object reference somewhere to display it later.
image_container = [''] * 64

for ind, square in enumerate(chessboard.squares):
    IS_DARK_SQUARE = ind in dark_squares
    row_num = abs(ind // 8 - 8)
    column_num = ind % 8
    if square == ' ':
        if IS_DARK_SQUARE:
            image_path = 'assets/dark_square.png'
        else:
            image_path = 'assets/light_square.png'
    elif square.color == 'white' or square.color == 'black':
        color = square.color
        piece_type = str(type(square)).split('.')[1].split("\'")[0].lower()

        image_path = ''.join(['assets/', color, '_', piece_type])

        if IS_DARK_SQUARE:
            image_path = ''.join([image_path, '_on_dark.png'])
        else:
            image_path = ''.join([image_path, '_on_light.png'])
    else:
        raise Exception(f'Square {ind}: contents invalid.')

    image_path = tk.PhotoImage(file=image_path)
    image_container[ind] = image_path

    button = tk.Button(
        root,
        image=image_path,
        highlightthickness=0,
        bd=0,
        borderwidth=0,
        #command=square.move_piece()
        )

    button.grid(column=column_num, row=row_num)




root.mainloop()


#container.pack(side='top', fill='both', expand=True)
#container.grid_rowconfigure(0, weight=1)
#container.grid_columnconfigure(0, weight=1)