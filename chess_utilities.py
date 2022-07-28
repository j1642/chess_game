'''
Import and export board states to and from a truncated version of Forsyth-
Edwards Notation (FEN).

Primarily written to easily transfer complex board positions into
board.Board.squares list for testing.
'''
import copy
#from time import gmtime, strftime
import board
import pieces

# TODO: expand this for saving game state using a 'Save' button?

def print_fen_to_terminal(fen_string):
    '''Prints a FEN string into the terminal as an ASCII chess board.
    Similar to board.Board.__repr__.
    '''
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
    '''Converts FEN string to board.Board object.'''
    chessboard = board.Board()
    fen = fen.split(' ')

    turn_to_move = fen.pop()
    if turn_to_move == 'w':
        last_move_color = 'black'
    elif turn_to_move == 'b':
        last_move_color = 'white'

    chessboard.last_move_piece = pieces.Pawn('placeholder', last_move_color, 100)

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
                piece = letter_to_piece[char.lower()](char, piece_color, squares_ind_counter)
                chessboard.squares[squares_ind_counter] = piece
                if piece.color == 'white':
                    chessboard.white_pieces.append(piece)
                    if isinstance(piece, pieces.King):
                        chessboard.white_king = piece
                elif piece.color == 'black':
                    chessboard.black_pieces.append(piece)
                    if isinstance(piece, pieces.King):
                        chessboard.black_king = piece
                squares_ind_counter += 1

            elif char.isdigit():
                # Set one or more squares equal to ' '.
                for _ in range(int(char)):
                    chessboard.squares[squares_ind_counter] = ' '
                    squares_ind_counter += 1

    return chessboard


def export_board_to_fen(chessboard):
    '''Convert board.Board.squares list to a FEN string, without castling, en
    passant, and move counts because they are not be used in these scripts.
    '''
    # Deepcopy seems necessary here because the original board is not equal to
    # and is not the board after calling this function, according to one of the
    # tests.
    squares = copy.deepcopy(chessboard.squares)
    fen = []
    for slice_start in range(0, 57, 8):
        slice_end = slice_start + 8
        fen.append(squares[slice_start:slice_end])

    fen = list(reversed(fen))
    # Add piece positions to fen
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

    #with open('FEN_exports.txt', 'a') as export:
     #   current_time = strftime('%Y-%m-%d %H:%M', gmtime())
      #  export.write(f'{current_time}\n')
       # export.write(f'{fen}\n\n')

    return fen


if __name__ == '__main__':
    import unittest

    class TestChessUtilities(unittest.TestCase):
        def test_export_board_to_fen(self):
            chessboard = board.Board()
            chessboard.initialize_pieces()
            #original_board = copy.deepcopy(chessboard)

            exported_fen = export_board_to_fen(chessboard)

            self.assertEqual(exported_fen,
                             'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w')
            # Test below fails so the export_board_to_fen function uses
            # copy.deepcopy.
            #self.assertEquals(original_board, chessboard)


        def test_import_fen_to_board(self):
            '''This is not a thorough test. The real test is visually examining
            the printed chessboard.
            '''
            check_test = 'rnbB2kr/1p1p3p/8/2pP2Q1/p3P3/P7/1PP2PPP/RN2KBNR b'
            chessboard = import_fen_to_board(check_test)

            # print(chessboard)
            self.assertIsInstance(chessboard.squares[0], pieces.Rook)
            self.assertEqual(chessboard.squares[0].color, 'white')



    unittest.main()
