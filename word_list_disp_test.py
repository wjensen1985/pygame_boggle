import pygame
from gui import *

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))

def disp_word_list(surface, word_list, pos, font, color):
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
        
playButton = Button((255,255,255), 550, 300, 400, 100, "Play Again")
mainMenuButton = Button((255,255,255), 550, 500, 400, 100, "Main Menu")
prevScore = Button((255,255,255), 550, 100, 400, 100, "Score: 10")
wordsFoundTxt = Button((100,100,255), 25, 50, 400, 100, "Words Found:")

# 50 px gap
# word list area: y1: 150px (+50?), x1: 50px (25?) --- x2: 500px y2: 650px
# dx = 450px = 150px each col

foundWords = ['start', 'test', 'aseghl', 'askldf', 'skdflsdjfk', 'sdklf','sjdkf','ksdfj' ,'ksdfj' ,'ksdfj' ,'ksdfj' ,'dkf','dkf','dkf','dkf','dkf','dkf','end']
print(len(foundWords))

while True:
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            pygame.quit()
            quit()
    
    screen.fill((100,100,255))

    # disp buttons:
    playButton.draw(screen)
    mainMenuButton.draw(screen)
    prevScore.draw(screen)
    wordsFoundTxt.draw(screen)

    # display found words list here:
    disp_word_list(screen, foundWords, (50,150), pygame.font.SysFont("Arial", 40), 'black')

    # update screen:
    pygame.display.update()