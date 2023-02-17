"""Import and export board states to and from a truncated version of
Forsyth-Edwards Notation (FEN).

Primarily written to convert board positions into board.Board objects for
debugging.

Functions
---------
    print_fen_to_terminal()
    import_fen_to_board()
    export_board_to_fen()
    pickle_and_add_board_to_db()
    load_board_from_db()
    create_board_database()

"""
import copy
import pickle
import sqlite3
from time import gmtime, strftime

import board
import pieces


# TODO: expand this for saving game state using a 'Save' button?

def print_fen_to_terminal(fen_string):
    """Print a FEN string into the terminal as an ASCII chess board.
    Similar to board.Board.__repr__.
    """
    fen_ls = fen_string.split(' ')
    fen_ls[0] = fen_ls[0].split('/')
    assert len(fen_ls[0]) == 8
    print(fen_ls)

    return_ls = []

    for row in fen_ls[0]:
        row_out = ['|']
        for char in row:
            if char.isalpha():
                row_out.append(char)
                row_out.append('|')
            elif char.isdigit():
                row_out.append(' |' * int(char))
        return_ls.append(''.join(row_out))

    for row in return_ls:
        print(row)


def import_fen_to_board(fen: str):
    """Convert FEN string to board.Board object."""
    chessboard = board.Board()
    fen = fen.split(' ')

    turn_to_move = fen.pop()
    if turn_to_move == 'w':
        last_move_color = 'black'
    elif turn_to_move == 'b':
        last_move_color = 'white'

    chessboard.last_move_piece = pieces.Pawn('placeholder',
                                             last_move_color,
                                             100)

    if fen[-1] == ' ':
        fen.pop()

    fen = fen[0].split('/')

    letter_to_piece = {'p': pieces.Pawn, 'n': pieces.Knight,
                       'b': pieces.Bishop, 'r': pieces.Rook,
                       'q': pieces.Queen, 'k': pieces.King}

    # Add pieces and empty squares to chessboard.squares.
    squares_ind_counter = 0
    fen = reversed(fen)
    for row in fen:
        for char in row:
            if char.isalpha():
                # Make a piece in chessboard.squares.
                if char.isupper():
                    piece_color = 'white'
                elif char.islower():
                    piece_color = 'black'
                piece = letter_to_piece[char.lower()](char,
                                                      piece_color,
                                                      squares_ind_counter)
                chessboard.squares[squares_ind_counter] = piece
                if piece.color == 'white':
                    if isinstance(piece, pieces.King):
                        chessboard.white_king = piece
                    else:
                        chessboard.white_pieces.append(piece)
                elif piece.color == 'black':
                    if isinstance(piece, pieces.King):
                        chessboard.black_king = piece
                    else:
                        chessboard.black_pieces.append(piece)
                squares_ind_counter += 1

            elif char.isdigit():
                # Set one or more squares equal to ' '.
                for _ in range(int(char)):
                    chessboard.squares[squares_ind_counter] = ' '
                    squares_ind_counter += 1

    # Kings must be last piece in piece lists for check to work.
    if chessboard.white_king:
        chessboard.white_pieces.append(chessboard.white_king)
    if chessboard.black_king:
        chessboard.black_pieces.append(chessboard.black_king)

    return chessboard


def export_board_to_fen(chessboard):
    """Convert board.Board.squares list to a truncated FEN string (without
    castling, en passant, and move count indicators).
    """
    # Deepcopy seems necessary here because the original board is not
    # equal to and is not the same board object after calling this
    # function, based on the tests.
    squares = copy.deepcopy(chessboard.squares)
    fen = []
    for slice_start in range(0, 57, 8):
        slice_end = slice_start + 8
        fen.append(squares[slice_start:slice_end])

    fen = list(reversed(fen))
    # Add piece positions
    for ind, row in enumerate(fen):
        partial_fen = []
        adjacent_empty_squares_count = 0
        for square in row:
            if square == ' ':
                adjacent_empty_squares_count += 1
            else:
                # Reset adjacent_empty_squares_count and add piece's name[0].
                if adjacent_empty_squares_count > 0:
                    partial_fen.append(str(adjacent_empty_squares_count))
                    adjacent_empty_squares_count = 0
                partial_fen.append(square.name[0])

        if adjacent_empty_squares_count > 0:
            partial_fen.append(str(adjacent_empty_squares_count))
        fen[ind] = ''.join(partial_fen)

    fen = '/'.join(fen)

    # Add who's turn it is to move.
    white_or_black_to_move = ''
    last_move_piece = chessboard.last_move_piece

    if last_move_piece is None:
        white_or_black_to_move = 'w'
    elif last_move_piece.color == 'black':
        white_or_black_to_move = 'w'
    elif last_move_piece.color == 'white':
        white_or_black_to_move = 'b'
    else:
        raise Exception(f'Invalid Board.last_move_piece: {last_move_piece}')

    fen = ' '.join([fen, white_or_black_to_move])

    # with open('FEN_exports.txt', 'a') as export:
    #    current_time = strftime('%Y-%m-%d %H:%M', gmtime())
    #    export.write(f'{current_time}\n')
    #    export.write(f'{fen}\n\n')

    return fen


def pickle_and_add_board_to_db(chessboard, e_type, e_val):
    """Serialize and store board.Board object in an sqlite database.

    Called after an error has occurred so the board object can be debugged
    easily.

    Note: Traceback object can't be stored in the database.
    ("InterfaceError... probably unsupported type." It would be nice to
    include but it is not necessary. Consider manually adding traceback
    as a string after error.
    """
    current_time = strftime('%Y-%m-%d %H:%M', gmtime())
    pickled_board = pickle.dumps(chessboard)

    con = sqlite3.connect('chessboards.sqlite')
    cur = con.cursor()
    fields = (current_time, e_type, e_val, pickled_board)
    cur.execute('''INSERT INTO chessboards
                ('date', 'error_type', 'error_value', 'board_obj')
                VALUES (?, ?, ?, ?)''', fields)

    con.commit()
    con.close()


def load_board_from_db(row_id=None):
    """As a default, pulls the most recent board.Board object and
    associated information from the database. The row_id parameter can
    select a specific row from the table if needed.
    """
    # Should this instead return cur.fetchall() for more obvious bugs
    # where multiple rows are returned? Or is that an unrealistic outcome?
    con = sqlite3.connect('chessboards.sqlite')
    cur = con.cursor()
    # There could be a row with an id of 0. Need to avoid "if 0:" scenario.
    if row_id is not None:
        cur.execute('SELECT * FROM chessboards WHERE id = ?', (row_id,))
        return cur.fetchone()
    else:
        cur.execute('''SELECT * FROM chessboards
                          WHERE id = (SELECT MAX(id) FROM chessboards)''')
        return cur.fetchone()

    con.close()


def create_board_database():
    """Create a SQLite database in the current directory, if a file named
    "chessboards.sqlite" does not already exist.
    """
    con = sqlite3.connect('chessboards.sqlite')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS chessboards
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date text,
                     error_type text,
                     error_value text,
                     board_obj)
                    ''')

    con.commit()
    con.close()


if __name__ == '__main__':
    import unittest

    class TestChessUtilities(unittest.TestCase):
        """chess_utilities.py tests"""

        def test_export_board_to_fen(self):
            """Board object is exportable to Forsyth-Edwards Notation (FEN)."""
            chessboard = board.Board()
            chessboard.initialize_pieces()
            # original_board = copy.deepcopy(chessboard)

            exported_fen = export_board_to_fen(chessboard)

            self.assertEqual(exported_fen,
                             'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w')
            # Test below fails so the export_board_to_fen function uses
            # copy.deepcopy.
            # self.assertEquals(original_board, chessboard)

        def test_import_fen_to_board(self):
            """Board imports without error. Requires visual check of the
            printed chessboard for a more detailed check.
            """
            check_test = 'rnbB2kr/1p1p3p/8/2pP2Q1/p3P3/P7/1PP2PPP/RN2KBNR b'
            chessboard = import_fen_to_board(check_test)

            # print(chessboard)
            self.assertIsInstance(chessboard.squares[0], pieces.Rook)
            self.assertEqual(chessboard.squares[0].color, 'white')

        def test_pickle_and_add_board_to_db(self):
            """Serialize the Board object and add it to the SQLite database."""
            chessboard = board.Board()
            chessboard.initialize_pieces()
            chessboard.squares[8].update_moves(chessboard)
            chessboard.squares[8].move_piece(chessboard, 24)

            con = sqlite3.connect('chessboards.sqlite')
            cur = con.cursor()
            cur.execute('SELECT COUNT(id) FROM chessboards')
            old_rows_in_db_count = cur.fetchall()[0][0]

            pickle_and_add_board_to_db(chessboard, self.e_type,
                                       self.e_val)

            cur.execute('SELECT COUNT(id) FROM chessboards')
            new_rows_in_db_count = cur.fetchall()[0][0]

            self.assertEqual(new_rows_in_db_count, old_rows_in_db_count + 1)

        def test_load_board_from_db(self):
            """Load the serialized Board object from the database to a
            useable object.
            """
            _, _, error_type, error_value, chessboard = load_board_from_db()
            chessboard = pickle.loads(chessboard)

            self.assertEqual(error_type, 'Exception')
            self.assertEqual(error_value, 'Raise Exception for tests.')
            self.assertIsInstance(chessboard.squares[24], pieces.Pawn)

            # Clean up database after tests.
            con = sqlite3.connect('chessboards.sqlite')
            cur = con.cursor()
            cur.execute('''DELETE FROM chessboards
                           WHERE id = (SELECT MAX(id) FROM chessboards)''')
            con.commit()
            con.close()

    unittest.main()
