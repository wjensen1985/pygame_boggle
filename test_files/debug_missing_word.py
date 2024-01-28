from boggle import *

test = Session()

boardLetters = [
    ['C', 'I', 'J', 'E'],
    ['S', 'E', 'O', 'F'],
    ['O', 'D', 'E', 'E'],
    ['I', 'S', 'P', 'L']
]

test.board.board = boardLetters
print(test.board.board)
test.board.solve_board(test.dictionary)

foundWords = list(test.board.solution_set)
print(sorted(foundWords))