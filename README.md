<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/5/52/Chess_Programming.svg" height=180 width=180>
</p>

<p align="center">
  <a href="https://github.com/j1642/chess_game/actions/workflows/test.yml">
    <img src="https://github.com/j1642/chess_game/actions/workflows/test.yml/badge.svg">
  </a>
</p>

A playable UCI chess engine.

### Features
- [UCI communication protocol](https://www.wbec-ridderkerk.nl/html/UCIProtocol.html)
([Universal Chess Interface](https://en.wikipedia.org/wiki/Universal_Chess_Interface))

- Board representation
  - 1D board array with separate piece lists. Hybrid of square- and piece-centric designs.
- Move generation
  - [Pseudo-legal](https://www.chessprogramming.org/Move_Generation#Pseudo-legal), legality checked during move tree traversal
  - [Perft and divide](https://www.chessprogramming.org/Perft) debugging functions
- Search
  - [Negamax](https://www.chessprogramming.org/Negamax) algorithm
  - [Alpha-beta](https://www.chessprogramming.org/Alpha-Beta) optimizations
  - [Transposition table](https://www.chessprogramming.org/Transposition_Table) based on [Zobrist hashing](https://www.chessprogramming.org/Zobrist_Hashing)
- Evaluation
  - Piece mobility
  - Pawn structure
  - [Piece square tables](https://www.chessprogramming.org/Piece-Square_Tables)
  - [Evaluation tapering](https://www.chessprogramming.org/Tapered_Eval)
 
### Use
Clone or unzip the repository (green Code button --> Download ZIP).
##### To play chess,
```
$ python3 game.py
```
##### To run the engine,
```
$ python3 engine.py
```

### Dependencies
- Python 3.6+
- Tkinter (to play against the computer)
