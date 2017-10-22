# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 10:07:28 2017

@author: Laurence
"""

import pygame
import numpy as np
from scipy import signal

gameMode = 'b' #b=beginner, i=intermediate, e=expert, c=custom
if gameMode == 'e':
    gridWidth = 30
    gridHeight = 16
    numMines = 99
elif gameMode == 'i':
    gridWidth = 16
    gridHeight = 16
    numMines = 40
elif gameMode == 'b':
    gridWidth = 8
    gridHeight = 8
    numMines = 10
elif gameMode == 'c': 
    '''large values can generate a recursion error if trying to reveal more than 
    "sys.getrecursionlimit()" surrounding zeros at once. Adjusting mine density 
    may help. Also program is probably not optimised enough to handle large boards'''
    gridWidth = 100
    gridHeight = 20
    numMines = 350  

pygame.init()

font = pygame.font.SysFont(None, 30) #30 = font size

def message_to_screen(text, color, x, y, align): #align: topleft, topright, center
    textSurface = font.render(text, True, color)
    textRect = textSurface.get_rect()
    if align == 'center':
        textRect.center = (x), (y)
    elif align == 'topleft':
        textRect.topleft = (x), (y)
    elif align == 'topright':
        textRect.topright = (x), (y)
    gameDisplay.blit(textSurface, textRect) 

barHeight = 40

tileWidth = 15
border = 1

displayWidth = tileWidth*gridWidth + border*(gridWidth+1)
displayHeight = tileWidth*gridHeight + border*(gridHeight+1) + barHeight

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight)) #screen size
pygame.display.set_caption('Minesweeper') #Window Title

clock = pygame.time.Clock()
fps = 60
keysDown = {}

white = (255, 255, 255)
black = (0, 0, 0)
gray = (192, 192, 192)     
red = (255, 0, 0)     

img = {0: pygame.image.load('img/0.png').convert_alpha(),
       1: pygame.image.load('img/1.png').convert_alpha(),
       2: pygame.image.load('img/2.png').convert_alpha(),
       3: pygame.image.load('img/3.png').convert_alpha(),
       4: pygame.image.load('img/4.png').convert_alpha(),
       5: pygame.image.load('img/5.png').convert_alpha(),
       6: pygame.image.load('img/6.png').convert_alpha(),
       7: pygame.image.load('img/7.png').convert_alpha(),
       8: pygame.image.load('img/8.png').convert_alpha(),
       9: pygame.image.load('img/mine.png').convert_alpha(),
       'flag': pygame.image.load('img/flag.png').convert_alpha(),
       'wrongFlag': pygame.image.load('img/incorrect_flag.png').convert_alpha(),
       'mineExplode': pygame.image.load('img/mine_explode.png').convert_alpha()}

faces = {'safe': pygame.image.load('img/safe.png').convert_alpha(),
         'suspense': pygame.image.load('img/suspense.png').convert_alpha(),
         'defeat': pygame.image.load('img/defeat.png').convert_alpha(),
         'victory': pygame.image.load('img/victory.png').convert_alpha()}
faceRect = pygame.Rect((displayWidth/2 - 11, barHeight/2 - 11), (23, 23)) #11 is ~half width of image (which is 23)


class Game():
    def __init__(self):
        self.gameExit = False
        self.numMines = numMines
        if self.numMines >= gridWidth*gridHeight:
            self.numMines = gridWidth*gridHeight - 1
            
        self.timerSeconds = 0
        
        self.reset()
        self.game_loop()
    
    def reset(self):
        self.grid = np.zeros((gridHeight, gridWidth))
        self.revealGrid = np.zeros((gridHeight, gridWidth)) #0=hidden, 1=revealed, 2=flag
        self.flagGrid = np.zeros((gridHeight, gridWidth)) #1=flag, 0=no flag, used in middle_click()
        self.flagCounter = self.numMines
        self.leftClickCounter = 0
        self.startTicks = pygame.time.get_ticks()
        self.numTilesRevealed = 0
        self.gameOver = False
        self.gameOverType = ''
        self.face = faces['safe']
        self.clickedMines = []
        
    def generate_board(self):
#        generate board --> first click can't be a mine
        linearSelection = self.column + self.row*gridWidth #convert 2d coordinates into linear coordinate
        
        values = np.random.choice(range(gridWidth*gridHeight), self.numMines, replace=False)
#        make sure first click isn't a mine
        if linearSelection in values:
            values = list(values)
            freeTiles = []
            for tile in range(gridWidth * gridHeight):
                if tile not in values:
                    freeTiles.append(tile)
            values.append(np.random.choice(freeTiles))
            values.remove(linearSelection)
        
#       np.put(self.grid, np.random.choice(range(gridWidth*gridHeight), self.numMines, replace=False), 1)
        np.put(self.grid, values, 1)
#        np.put(input grid, [locations to change - can reference as if grid was a 1 dimensional array], number to change location to)
#        np.random.choice(random numbers chosen from elements of this input, num replacements to make, false makes numbers different each time)
         
        conv = signal.convolve(self.grid, np.ones((3,3)), mode='same')
        self.grid = self.grid.astype(np.bool)
        conv[self.grid] = 9
        self.grid = conv.astype(np.int32)    
        
    def render(self):
        if not self.gameOver:
            self.timerSeconds = (pygame.time.get_ticks() - self.startTicks)/1000
        gameDisplay.fill(black) 
        pygame.draw.rect(gameDisplay, gray, (0, 0, displayWidth, barHeight))
        gameDisplay.blit(self.face, faceRect) 
        message_to_screen('{}'.format(self.flagCounter), red, 5, 5, 'topleft')
        message_to_screen('{:.0f}'.format(self.timerSeconds),red, 
                          displayWidth-5, 5, 'topright')
                
        for row in range(gridHeight):
            for column in range(gridWidth):
                if self.revealGrid[row, column] == 1:
                    image = img[self.grid[row, column]]
                elif self.revealGrid[row, column] == 2:
                    #coordinate is flagged
                    image = img['flag']
                else:
                    #coordinate not revealed
                    tileX = (border + tileWidth) * column + border
                    tileY = (border + tileWidth) * row + border + barHeight
                
                    pygame.draw.rect(gameDisplay, white, (tileX, tileY, 
                                                      tileWidth, tileWidth))
                    continue
                    
                gameDisplay.blit(image, ((border + tileWidth)*column + border,
                                         (border +tileWidth )*row + border + barHeight))
        if self.gameOver and self.gameOverType == 'defeat':
            for coordinate in self.hiddenMines:
                image = img[9]
                gameDisplay.blit(image, ((border + tileWidth)*coordinate[1] + border,
                                         (border +tileWidth )*coordinate[0] + border + barHeight))
            for coordinate in self.wrongFlagCoordinates:
                image = img['wrongFlag']
                gameDisplay.blit(image, ((border + tileWidth)*coordinate[1] + border,
                                         (border +tileWidth )*coordinate[0] + border + barHeight))
            for coordinate in self.clickedMines:
                image = img['mineExplode']
                gameDisplay.blit(image, ((border + tileWidth)*coordinate[1] + border,
                                         (border +tileWidth )*coordinate[0] + border + barHeight))
                
    def game_over(self, type_): #type = 'defeat' or 'victory'
        self.gameOverType = type_
        self.gameOver = True
        self.gameTime = (pygame.time.get_ticks() - self.startTicks)/1000
        self.timerSeconds = self.gameTime
        if type_ == 'victory':
            self.face = faces['victory']
            self.reveal_everything()            
            
        elif type_ == 'defeat':
            self.revealGrid[self.row, self.column] = 1
            self.face = faces['defeat']
            
            self.wrongFlagCoordinates = []
            self.hiddenMines = []
            for row in range(gridHeight):
                for column in range(gridWidth):
                    if self.grid[row, column] != 9 and self.revealGrid[row, column] == 2:
                        self.wrongFlagCoordinates.append([row, column])
                    elif self.grid[row, column] == 9 and self.revealGrid[row, column] !=2:
                        self.hiddenMines.append([row, column])
            
            
    def reveal_surrounding(self, row, column):
        for sCol in range(-1, 2):
            for sRow in range(-1, 2):
                if row+sRow < 0 or row+sRow > gridHeight-1 or column+sCol < 0 \
                or column+sCol > gridWidth-1:
                    continue
                if self.revealGrid[row+sRow, column+sCol] == 0:
                    if self.grid[row+sRow, column+sCol] == 9:
                        self.game_over('defeat')
                        self.clickedMines.append([row+sRow, column+sCol])
                        continue
                    self.revealGrid[row+sRow, column+sCol] = 1
                    self.numTilesRevealed += 1
                    if self.grid[row+sRow, column+sCol] == 0:
                        self.reveal_surrounding(row+sRow, column+sCol)
                        
        self.check_victory()
                                     
    def reveal(self):
        if self.revealGrid[self.row, self.column] == 0: #make sure tile isn't a flag and isn't revealed
            if self.grid[self.row, self.column] == 9:
                self.game_over('defeat')
                self.clickedMines.append([self.row, self.column])
            elif self.grid[self.row, self.column] == 0:
#                reveal all surrounding zeros
                self.reveal_surrounding(self.row, self.column)
                    
            else:
                self.revealGrid[self.row, self.column] = 1
                self.numTilesRevealed += 1
            
        self.check_victory()
        
    def reveal_everything(self):
        for row in range(gridHeight):
            for column in range(gridWidth):
                if self.grid[row, column] == 9:
                    self.revealGrid[row, column] = 2
                else:
                    self.revealGrid[row, column] = 1
        self.flagCounter = 0
        
    def check_victory(self):
        if self.numTilesRevealed == gridWidth*gridHeight - self.numMines:
            self.game_over('victory')

    def left_click(self):
        if self.leftClickCounter == 0: #first click
            self.generate_board()
            self.reveal()
        else:
            self.reveal()
        self.leftClickCounter += 1
            
    def right_click(self):
        if self.revealGrid[self.row, self.column] == 2:
            self.revealGrid[self.row, self.column] = 0
            self.flagGrid[self.row, self.column] = 0
            self.flagCounter += 1
        elif self.revealGrid[self.row, self.column] == 0:
            self.revealGrid[self.row, self.column] = 2
            self.flagGrid[self.row, self.column] = 1
            self.flagCounter -= 1
        
    def middle_click(self):
        #make sure coordinaet is revealed and no point doing anything if coordinate is a 0
        if self.revealGrid[self.row, self.column] == 1 \
        and self.grid[self.row, self.column] != 0:
            conv = signal.convolve(self.flagGrid, np.ones((3,3)), mode='same')
            #make sure number of flags surrounding is number on square
            if conv[self.row, self.column] == self.grid[self.row, self.column]:
                self.reveal_surrounding(self.row, self.column)      
            
    def real_position_to_coordinates(self, pos):
        self.row = (pos[1] - barHeight) // (tileWidth + border)
        self.column = pos[0] // (tileWidth + border)
        #solve issue where you can click outsie of grid range
        if self.row >= gridHeight:
            self.row = gridHeight-1
        if self.column >= gridWidth:
            self.column = gridWidth-1        

    def game_loop(self):
        while not self.gameExit:
#            EVENT AND INPYT HANDLING
            for event in pygame.event.get():           
                if event.type == pygame.QUIT:
                    self.gameExit = True
                    
                if event.type == pygame.KEYDOWN:
                    keysDown[event.key] = True
                if event.type == pygame.KEYUP: 
                    if event.key in keysDown:
                        del keysDown[event.key]
                    if event.key == pygame.K_F2:
                        self.reset()
                    if event.key == pygame.K_r:
                        self.reveal_everything()
                        
                if event.type == pygame.MOUSEBUTTONDOWN and not self.gameOver:
                    keysDown[event.button] = True
                    pos = pygame.mouse.get_pos()
                    if event.button == 3 and pos[1] >= barHeight:
                        self.real_position_to_coordinates(pos)
                        self.right_click()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    button = event.button #left click = 1, middle = 2 right click = 3
                    pos = pygame.mouse.get_pos()
                        
                    if faceRect.collidepoint(pos) and button ==1:
                        self.reset()
                    if pos[1] >= barHeight and not self.gameOver:
                        self.real_position_to_coordinates(pos)
                        
#                        to detect both left and right detect 2 held down then trigger when one releases
                        if 1 in keysDown and 3 in keysDown:
                            if button == 1 or button == 3:
                                self.middle_click()
                        elif button == 2:
                            self.middle_click()
                        elif button == 1:
                            self.left_click()
                    
                    if button in keysDown:   
                            del keysDown[button]
                            
                if not self.gameOver:            
                    if 1 in keysDown:
                        if not faceRect.collidepoint(pos):
                            self.face = faces['suspense']
                    else:
                        self.face = faces['safe']
                            
                            
            self.render()
            pygame.display.update()
            clock.tick(fps) #frames per second
        
        pygame.quit()
        quit()
        
if __name__ == '__main__':     
    Game()