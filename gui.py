import pygame
import time
from boggle import *

class Button:
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.SysFont('Arial', 60)

    def draw(self,win,outline=None, border_radius=0):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),border_radius)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),border_radius)
        
        if self.text != '':
            text = self.font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False
    
class GameTileButton(Button):
    def __init__(self, color, x, y, width, height, text=''):
        super().__init__(color, x, y, width, height, text)
        self.used = False
        self.width = 100
        self.height = 100
        self.selectedColor = (255,100,0) #orange
        self.unselectedColor = (255,255,255)
        self.hoverColor = (225,125,125)
        self.stateColor = self.unselectedColor
        self.prevStateTime = 0
    
    def change_state(self):
        if self.used:
            self.used = False
            self.stateColor = self.unselectedColor
            self.color = self.stateColor
        else:
            self.used = True
            self.stateColor = self.selectedColor
            self.color = self.stateColor
    
    def __repr__(self):
        return self.text
                        
class Game():
    def __init__(self):
        pygame.init()

        # set screen dimensions
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 700

        # set game settings and start up variables
        self.time_limit = 180
        self.isOpen = True
        self.useKeyboard = False
        self.text_box = []
        self.timerDisp = self.time_limit


        # Create the screen object
        # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        # loading screen and window caption:
        self.SCREEN.fill((100,100,255))
        self.loading_msg = Button((100,100,255), 250, 250, 500, 200, "Loading")
        self.loading_msg.draw(self.SCREEN)
        pygame.display.set_caption("Boggle")
        pygame.display.update()

        # create Session object:
        # (has letter states for current board)
        self.gameSession = Session()

        # create gui board object (grid of gametile buttons, gui only)
        self.gui_board = [[None]*4 for _ in range(self.gameSession.board.size)]
        self.make_gui_board()

        # flags for if the game is in the after game or in game state, this helps prevent hanging loops if quitting pygame (will keep going in curr window loop otherwise and would throw pygame updating display error when closing the game)
        self.inGame = False
        self.inAfterGame = False

    # creates grid of gametilebutton objects
    def make_gui_board(self):
        gx, gy = 0, 0
        for i in range(400,self.SCREEN_WIDTH - 100, (self.SCREEN_WIDTH-500) // 4):
            gx = 0
            for j in range(100, self.SCREEN_HEIGHT - 100, (self.SCREEN_HEIGHT-200)//4):
                self.gui_board[gx][gy] = GameTileButton((255,255,255), i, j, 100, 100, self.gameSession.board.board[gx][gy])
                gx += 1
            gy += 1
    
    # draws gui board to pygame screen
    def disp_gui_board(self):
        for r in range(len(self.gui_board)):
            for c in range(len(self.gui_board[r])):
                self.gui_board[r][c].draw(self.SCREEN, (0,0,0))
        
    def reset_game_tile_states(self):
        for i in range(len(self.gui_board)):
            for j in range(len(self.gui_board[i])):
                if self.gui_board[i][j].used:
                    self.gui_board[i][j].change_state()

    def game_loop(self):
        # Game set up:
        score = 0
        foundWords = set()

        # Buttons LIsted in graphical order (top to bottom)
        # Timer Label
        timerLabelBox = Button((100,100,255), 50, 150, 300, 50, "Time Left:")
        timerLabelBox.font = pygame.font.SysFont('Arial', 40)
        # time left:
        timerBox = Button((255,255,255), 150, 200, 100, 100, str(self.time_limit))
        # current score:
        scoreBox = Button((255,255,255), 50, 325, 300, 100, "Score: " + str(score))
        # pop up messages (word correct/incorrect)
        msgBox = Button((100,100,255), 50, 450, 300, 50, "")
        msgBox.font = pygame.font.SysFont('Arial', 40)
        # current word string
        textBox = Button((255,255,255), 50, 500, 300, 100, "".join(self.text_box))
        textBox.font = pygame.font.SysFont('Arial', 40)
        # switch between using keyboard/mouse button
        switchCtrlsBtn = Button((225,255,255), 50, 50, 300, 50, "Use Mouse" if self.useKeyboard else "Use Keyboard")
        switchCtrlsBtn.font = pygame.font.SysFont('Arial', 40)


        self.gameSession.board.solution_set.clear()
        self.gameSession.board.shuffle()
        self.gameSession.board.solve_board(self.gameSession.dictionary)

        self.make_gui_board()

        start_time = time.time()
        running = True

        # (re)sets last state update of gametilebuttons to 0, this is for mouse hover & button clicked color changes
        for i in range(len(self.gui_board)):
            for j in range(len(self.gui_board[i])):
                self.gui_board[i][j].prevStateTime = 0

        #start game/event handler loop
        while running:
            elapsed_time = time.time() - start_time
            if elapsed_time > self.time_limit:
                timerBox.text = str(int(self.time_limit))
                running = False
                continue

            textBox.text = "".join(self.text_box)
            timerBox.text = str(self.time_limit - int(elapsed_time))
            scoreBox.text = "Score: " + str(score)
            
            self.SCREEN.fill((100,100,255))

            #draw board background
            pygame.draw.rect(self.SCREEN, (255,174,66), (375,75,525,525))
            
            #draw graphic elements:
            # letter tiles 
            self.disp_gui_board()
            # current text
            textBox.draw(self.SCREEN)
            # timer
            timerBox.draw(self.SCREEN)
            # score
            scoreBox.draw(self.SCREEN)
            # pop up messages
            msgBox.draw(self.SCREEN)
            # Timer Label Text:
            timerLabelBox.draw(self.SCREEN)
            # change between using keyboard/mouse button
            switchCtrlsBtn.draw(self.SCREEN)

            #update display
            pygame.display.update()

            # pygame event handler:
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    self.isOpen = False
                    break

                # mouse clicks for buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.useKeyboard:
                        for i in range(len(self.gui_board)):
                            for j in range(len(self.gui_board[i])):
                                if self.gui_board[i][j].isOver(pos):
                                    if not self.gui_board[i][j].used:
                                        self.text_box.append(self.gui_board[i][j].text)
                                    else:
                                        # submit word guess with current string
                                        isWord = self.gameSession.board.check_word_guess("".join(self.text_box))
                                        if isWord:
                                            if ("".join(self.text_box)) in foundWords:
                                                msgBox.text = "Word already found"
                                            else:
                                                foundWords.add("".join(self.text_box))
                                                wordScore = max(1, len(self.text_box) - 3)
                                                msgBox.text = "Word Score: " + str(wordScore)
                                                score += wordScore
                                        else:
                                            msgBox.text = "Not a word!"
                                        self.text_box = []

                                        # need to reset state of all gameTileButtons
                                        self.reset_game_tile_states()

                                        continue

                                    self.gui_board[i][j].change_state()
                                    self.gui_board[i][j].prevStateTime = elapsed_time

                    # check for options button (to switch self.useKeyboard), will always be active:
                    if switchCtrlsBtn.isOver(pos):
                        self.useKeyboard = not self.useKeyboard
                        switchCtrlsBtn.text = "Use Mouse" if self.useKeyboard else "Use Keyboard"
                        self.reset_game_tile_states()
                        self.text_box = []

                # MOUSE HOVERS (for buttons)
                if not self.useKeyboard:
                    # MOUSE HOVERS (for buttons)
                    if event.type == pygame.MOUSEMOTION:
                        for i in range(len(self.gui_board)):
                            for j in range(len(self.gui_board[i])):
                                if self.gui_board[i][j].isOver(pos) and not self.gui_board[i][j].used and (elapsed_time - self.gui_board[i][j].prevStateTime) > 0.5:
                                    self.gui_board[i][j].color = self.gui_board[i][j].hoverColor
                                else:
                                    self.gui_board[i][j].color = self.gui_board[i][j].stateColor
                
                # switchCtrlsBtn Hover color change
                if event.type == pygame.MOUSEMOTION:
                    if switchCtrlsBtn.isOver(pos):
                        switchCtrlsBtn.color = (225,125,125)
                    else:
                        switchCtrlsBtn.color = (255,255,255)

                # keyboard typing events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE and self.useKeyboard:
                        if self.text_box:
                            self.text_box.pop()


                    elif event.key == pygame.K_RETURN and self.useKeyboard:
                        # guess word
                        isWord = self.gameSession.board.check_word_guess("".join(self.text_box))
                        if isWord:
                            if ("".join(self.text_box)) in foundWords:
                                msgBox.text = "Word already found"
                            else:
                                foundWords.add("".join(self.text_box))
                                wordScore = max(1, len(self.text_box) - 3)
                                msgBox.text = "Word Score: " + str(wordScore)
                                score += wordScore
                        else:
                            msgBox.text = "Not a word!"
                        self.text_box = []

                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    
                    elif len(self.text_box) < 16 and self.useKeyboard:
                        if event.key == pygame.K_a:
                            self.text_box.append("A")
                        elif event.key == pygame.K_b:
                            self.text_box.append("B")
                        elif event.key == pygame.K_c:
                            self.text_box.append("C")
                        elif event.key == pygame.K_d:
                            self.text_box.append("D")
                        elif event.key == pygame.K_e:
                            self.text_box.append("E")
                        elif event.key == pygame.K_f:
                            self.text_box.append("F")
                        elif event.key == pygame.K_g:
                            self.text_box.append("G")
                        elif event.key == pygame.K_h:
                            self.text_box.append("H")
                        elif event.key == pygame.K_i:
                            self.text_box.append("I")
                        elif event.key == pygame.K_j:
                            self.text_box.append("J")
                        elif event.key == pygame.K_k:
                            self.text_box.append("K")
                        elif event.key == pygame.K_l:
                            self.text_box.append("L")
                        elif event.key == pygame.K_m:
                            self.text_box.append("M")
                        elif event.key == pygame.K_n:
                            self.text_box.append("N")
                        elif event.key == pygame.K_o:
                            self.text_box.append("O")
                        elif event.key == pygame.K_p:
                            self.text_box.append("P")
                        elif event.key == pygame.K_q:
                            self.text_box.append("Q")
                        elif event.key == pygame.K_r:
                            self.text_box.append("R")
                        elif event.key == pygame.K_s:
                            self.text_box.append("S")
                        elif event.key == pygame.K_t:
                            self.text_box.append("T")
                        elif event.key == pygame.K_u:
                            self.text_box.append("U")
                        elif event.key == pygame.K_v:
                            self.text_box.append("V")
                        elif event.key == pygame.K_w:
                            self.text_box.append("W")
                        elif event.key == pygame.K_x:
                            self.text_box.append("X")
                        elif event.key == pygame.K_y:
                            self.text_box.append("Y")
                        elif event.key == pygame.K_z:
                            self.text_box.append("Z")
                    elif self.useKeyboard:
                        # print("guess too long already")
                        msgBox.text = "Guess too long already"    


                    # print("curr string: " + "".join(self.text_box))


        self.inGame = False
        self.inAfterGame = True
        self.text_box = []

        output = [score, foundWords]
        return output    

    def main_menu(self):
        running = True
        playButton = Button((255,255,255), 250, 250, 500, 200, "Play")
        newGame = False

        while running:
            if self.inGame:
                outputs = self.game_loop()
            
            if self.inAfterGame:
                newGame = self.after_game(outputs)


            if newGame:
                self.inGame = True
                continue
            
            if not self.isOpen:
                running = False
                pygame.quit()
                break
            
            # disp menu:
            self.SCREEN.fill((100,100,255))

            # disp buttons:
            playButton.draw(self.SCREEN)
            
            # update screen:
            pygame.display.update()

            # event handler
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    break

                # mouse clicks for buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if playButton.isOver(pos):
                        # print("play button clicked")
                        self.inGame = True

        return

    # display list of words:
    def disp_word_list(self, surface, word_list, pos, font, color):
        x, y = pos
        col_width = 225
        cols = 0
        for word in word_list:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if y >= 650:
                y = pos[1]
                cols += 1
            x = pos[0] + (col_width * cols)
            surface.blit(word_surface, (x, y))
            y += word_height

    def after_game(self, input):
        if not self.isOpen:
            return False

        score, foundWordsSet = input
        foundWords = list(foundWordsSet)
        scoreStr = "Score: " + str(score)

        running = True

        # set up display buttons
        playButton = Button((255,255,255), 550, 300, 400, 100, "Play Again")
        mainMenuButton = Button((255,255,255), 550, 500, 400, 100, "Main Menu")
        prevScore = Button((255,255,255), 550, 100, 400, 100, scoreStr)
        wordsFoundTxt = Button((100,100,255), 25, 50, 400, 100, "Words Found:")

        while running:
            # disp menu:
            self.SCREEN.fill((100,100,255))

            # disp buttons:
            playButton.draw(self.SCREEN)
            mainMenuButton.draw(self.SCREEN)
            prevScore.draw(self.SCREEN)
            wordsFoundTxt.draw(self.SCREEN)

            # display found words list here:
            self.disp_word_list(self.SCREEN, foundWords, (50,150), pygame.font.SysFont("Arial", 40), 'black')

            # update screen:
            pygame.display.update()
            
            # pygame event handler:
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    self.isOpen = False
                    break

                # mouse clicks for buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if playButton.isOver(pos):
                        # print("play button clicked")
                        self.inAfterGame = False
                        return True
                    
                    if mainMenuButton.isOver(pos):
                        # print("main menu clicked")
                        self.inAfterGame = False
                        return False


        self.inAfterGame = False
        return False

if __name__ == "__main__":
    g = Game()
    g.main_menu()