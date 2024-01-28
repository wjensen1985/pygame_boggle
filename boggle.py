import csv
import random
import pickle
import os

class letter_die:
    def __init__(self, possible_letters = None):
        if possible_letters is None:
            self.possible_letters = []
        self.possible_letters = possible_letters
        self.current_letter = None

    def set_possible_letters(self, letters):
        self.possible_letters = []

        for i in range(len(letters)):
            self.possible_letters.append(letters[i])

    def set_current_letter(self, letter_index):
        if letter_index < len(self.possible_letters):
            self.current_letter = self.possible_letters[letter_index]
        else:
            print("index out large, not enough possible letters")
    
    def __repr__(self):
        error_msg = "current_letter is not set"

        if self.current_letter:
            return self.current_letter
        else:
            return error_msg

# 
class GameBoard:
    def __init__(self, size):
        self.size = size
        self.dice = self.tile_set_up(self.size)
        
        # is 2d grid of self.size x self.size
        self.board = self.board_set_up(self.dice, self.size)

        self.letterPositions = {}
        self.neighbors = {}

        self.solution_set = set()

        self.set_letter_positions()
        self.set_neighbors()

    def shuffle(self):
        self.dice = self.tile_set_up(self.size)
        self.board = self.board_set_up(self.dice, self.size)
        #print(self)

    def tile_set_up(self, board_size):
        letter_dice = []

        f = open('english_classic_boggle.csv', 'r')
        reader = csv.reader(f)
        possible_letters = []

        for row in reader:
            possible_letters.append(row)

        for i in range(board_size ** 2):
            die = letter_die(possible_letters[i])
            letter_dice.append(die)


        return letter_dice

    def board_set_up(self, dice, board_size):
        board = []

        for die in dice:
            die.set_current_letter(random.randint(0,5))

        for i in range(board_size):
            board.append([])
            for j in range(board_size):
                index = i*4 + j
                board[i].append(dice[index].current_letter)

        return board
    
    # prints current board in cmd line with lines/spacers 
    def __repr__(self):
        return '\n---------------------\n'.join([' | '.join(" Qu" if c =='QU' else " " + str(c) + " " for c in row) for row in self.board])
    
    def set_letter_positions(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] in self.letterPositions:
                    self.letterPositions[self.board[i][j].upper()].append((i*4 + j))
                else:
                    self.letterPositions[self.board[i][j].upper()] = [(i*4 + j)]
    
    def set_neighbors(self):
        for i in range(self.size**2):

            checks = [i-5, i-4, i-3, i-1, i+1, i+3, i+4, i+5]
            i_right = [7,4,2]
            i_left = [5,3,0]

            if (i+1)%4 == 0:
                for k in range(len(i_right)):
                    del checks[i_right[k]]
            if (i)%4 == 0:
                for k in range(len(i_left)):
                    del checks[i_left[k]]

            for j in range(len(checks)):
                if 0 <= checks[j] <= 15:
                    self.neighbors.setdefault(i, []).append(checks[j])
        # print(self.neighbors)

    def check_word_guess(self, guess):
        if guess in self.solution_set:
            return True
        else:
            return False

    def solve_board(self, preFixTrie):
        visited = set()
        directions = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,1], [1,-1], [1,0], [1,1]]

        def dfs(i, j, curPath):
            if i < 0 or i >= len(self.board) or j < 0 or j >= len(self.board):
                return
            if (i, j) in visited:
                return

            ####### MAKE CURR PATH A LIST OF TUPLES WITH THE I,J POSITION OF EACH LETTER, THEN MAKE A VARIABLE WITH CURRSTRING, WHICH HAS THE CURRENT LETTER STRING
            ####### THIS WAY CAN HAVE THE PATH SO WHEN DISPLAYING ANSWERS LATER, CAN DISPLAY THE ANSWER PATH WHEN ANSWER WORD IS CLICKED

            curString = "".join(curPath)
            #add a check here w/Trie so that can cut off calls that won't ever result in a word
            if not preFixTrie.startsWith(curString):
                return
            
            curPath.append(self.board[i][j])
            curString = "".join(curPath)

            # if len(curPath) == 4 and curPath[1] == 'E' and curPath[2] == 'E':
            #     print(f'i: {i}, j: {j}, curPath: {curPath}, curString: {curString}')
            
            #if curPath is a word in trie dict, then add to results
            if preFixTrie.search(curString) and len(curString) > 2:
                #need to add string, prev add argument: tuple(curPath.copy())
                self.solution_set.add(curString)
            visited.add((i,j))

            for dy, dx in directions:
                dfs(i+dy, j+dx, curPath)

            if len(curPath) > 0:
                curPath.pop()
            if (i,j) in visited:
                visited.remove((i,j))
            return

        for i in range(4):
            for j in range(4):
                dfs(i,j,[])
                    
        return

class TrieNode():
    def __init__(self):
        self.children = {}
        self.isWord = False

class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        curr = self.root
        for c in word:
            #add letter
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]
        curr.isWord = True
            
    def search(self, word: str) -> bool:
        curr = self.root
        for c in word:
            if c not in curr.children:
                return False
            curr = curr.children[c]
        if curr.isWord == True:
            return True
        return False

    def startsWith(self, prefix: str) -> bool:
        curr = self.root
        for c in prefix:
            if c not in curr.children:
                return False
            curr = curr.children[c]
        return True

# Session object instantiates a GameBoard Object and has the function for cmd line game play
# the Session (and its GameBoard) can be used separately to set up the board and dictionary
# for play in other files(gui.py)
class Session():
    def __init__(self):
        # init GameBoard object
        self.board = GameBoard(4)

        # load in saved preFixTrie from .pkl file if it exists, else create one
        if not os.path.exists('preFixTrie.pickle'):
            self.createDict()
            with open('preFixTrie.pickle','rb') as f:
                self.dictionary = pickle.load(f)
        else:
            with open('preFixTrie.pickle', 'rb') as f:
                self.dictionary = pickle.load(f)

    # function to create a preFixTrie and pickle the object to disc
    # after being created once, this object will be loaded in to self.dictionary
    def createDict(self):
        f = open("words_alpha.txt","r")
        all_words_list = f.read().splitlines()
        preFixTrie = Trie()
        for w in all_words_list:
            preFixTrie.insert(w.upper())
        
        with open('preFixTrie.pickle', 'wb') as f:
            pickle.dump(preFixTrie, f)
    
    # function for cmd lien game play
    def startGame(self):
        self.board.solution_set.clear()
        self.board.shuffle()
        self.board.solve_board(self.dictionary)
        print(self.board)

        print("game started")
        score = 0
        guess_limit = 3
        guesses = 0

        while True:
            if guesses >= guess_limit:
                break
            w = input("enter word: ").upper()
            guesses += 1
            guessResult = self.board.check_word_guess(w)
            
            if guessResult:
                print("is a word")
                score += len(w)
            print("score: " + str(score))

        print("all guesses used, game is over")
        print("final score: " + str(score))

        return

# main function for this file, can play a cmd line version of boggle w/3 guesses per board
def main():
    game = Session()
    print("game and dict loaded")

    game.startGame()

    while 1:
        response = input("Play another game? (y/n): ")
        if response == 'y':
            game.startGame()
        else:
            break
    return

if __name__ == "__main__":
    main()