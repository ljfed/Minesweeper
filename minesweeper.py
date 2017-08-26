# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 10:07:28 2017

@author: Laurence
"""

'''
Dimensions:
Expert: 30x16, 99 mines
Intermediate: 16x16, 40 mines
Beginner: 8x8, 10 mines
'''

import pygame
import numpy as np
from scipy import signal

pygame.init()

white = (255, 255, 255)
#flagColor = (240, 23, 175)
flagColor = (255, 150, 14)

colors = {0: (192, 192, 192), #gray
          1: (0, 0, 255), #blue
          2: (0,128,0), #green
          3: (255, 0, 0), #red
          4: (0, 0, 128), #darkBlue
          5: (128, 0, 0), #darkRed
          6: (42, 148, 148), #lightBlue
          7: (0, 0, 0), #black
          8: (128, 128, 128), #lightgray
          9: (255, 201, 14)} #yellow

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

tileWidth = 20
border = 2

gridWidth = 8
gridHeight = 8

displayWidth = tileWidth*gridWidth + border*(gridWidth+1)
displayHeight = tileWidth*gridHeight + border*(gridHeight+1) + barHeight

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight)) #screen size
pygame.display.set_caption('Minesweeper') #Window Title

clock = pygame.time.Clock()
fps = 30
keysDown = {}

##picture
#imageList = ['safe', 'suspense', 'defeat', 'victory']
#image = pygame.image.load('img/' + imageList[0] + '.png').convert_alpha()
#imageX = (displayWidth)/2 - 30
#imageY = 0


class Game():
    def __init__(self):
        self.gameExit = False
        self.numMines = 10
        if self.numMines >= gridWidth*gridHeight:
            self.numMines = gridWidth*gridHeight - 1
            
        self.timerSeconds = 0
        
        self.reset()
        self.game_loop()
    
    def reset(self):
        self.grid = np.zeros((gridHeight, gridWidth))
        self.flagGrid = np.zeros((gridHeight, gridWidth))
        self.flagCounter = self.numMines
        self.leftClickCounter = 0
        self.startTicks = pygame.time.get_ticks()
        self.numTilesRevealed = 0
        self.gameOver = False
        
    def generate_board(self, row, column):
#        generate board --> first click can't be a mine
        linearSelection = column + row*gridWidth #convert 2d coordinates into linear coordinate
        
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
        self.grid = conv    
        
    def render(self):
        if not self.gameOver:
            self.timerSeconds = (pygame.time.get_ticks() - self.startTicks)/1000
        gameDisplay.fill(colors[7]) 
        pygame.draw.rect(gameDisplay, colors[0], (0, 0, displayWidth, barHeight))    
        message_to_screen('{}'.format(self.flagCounter), colors[3], 5, 5, 'topleft')
        message_to_screen('{:.0f}'.format(self.timerSeconds), colors[3], 
                          displayWidth-5, 5, 'topright')
                
        for row in range(gridHeight):
            for column in range(gridWidth):
                if self.flagGrid[row, column] == 1:
                    color = colors[self.grid[row, column]]
                elif self.flagGrid[row, column] == 2:
                    #coordinate is flagged
                    color = flagColor
                else:
                    #coordinate not revealed
                    color = white
                    
                tileX = (border + tileWidth) * column + border
                tileY = (border + tileWidth) * row + border + barHeight
                
                pygame.draw.rect(gameDisplay, color, (tileX, tileY, 
                                                      tileWidth, tileWidth))
                
#        gameDisplay.blit(image, (imageX, imageY))
                
    def reveal_surrounding(self, row, column):
        for sCol in range(-1, 2):
            for sRow in range(-1, 2):
                if row+sRow < 0 or row+sRow > gridHeight-1 or column+sCol < 0 \
                or column+sCol > gridWidth-1:
                    continue
                if self.flagGrid[row+sRow, column+sCol] == 0:
                    self.flagGrid[row+sRow, column+sCol] = 1
                    self.numTilesRevealed += 1
                    if self.grid[row+sRow, column+sCol] == 0:
                        self.reveal_surrounding(row+sRow, column+sCol)
                                     
    def reveal(self, row, column):
        if self.flagGrid[row, column] == 0: #make sure tile isn't a flag and isn't revealed
            if self.grid[row, column] == 9:
                print('DEFEAT')
                self.gameOver = True
                self.flagGrid[row, column] = 1
            elif self.grid[row, column] == 0:
#                reveal all surrounding zeros
                self.reveal_surrounding(row, column)
                    
            else:
                self.flagGrid[row, column] = 1
                self.numTilesRevealed += 1
            
        self.check_victory()
        
    def reveal_everything(self):
        for row in range(gridHeight):
            for column in range(gridWidth):
                if self.grid[row, column] == 9:
                    self.flagGrid[row, column] = 2
                else:
                    self.flagGrid[row, column] = 1
        self.flagCounter = 0
        
    def check_victory(self):
        print(self.numTilesRevealed)
        if self.numTilesRevealed == gridWidth*gridHeight - self.numMines:
            print('VICTORY')
            self.gameOver = True

    def left_click(self, row, column):
        print('Left Click At: {}, {}'.format(row, column)) 
        if self.leftClickCounter == 0: #first click
            self.generate_board(row, column)
            self.reveal(row, column)
        else:
            self.reveal(row, column)
        self.leftClickCounter += 1
            
    def right_click(self, row, column):
        print('Right Click At: {}, {}'.format(row, column))
        if self.flagGrid[row, column] == 2:
            self.flagGrid[row, column] = 0
            self.flagCounter += 1
        elif self.flagGrid[row, column] == 0:
            self.flagGrid[row, column] =2
            self.flagCounter -= 1
        
    def middle_click(self, row, column):
        print('Middle Click At: {}, {}'.format(row, column))
        

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
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    keysDown[event.button] = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    button = event.button #left click = 1, middle = 2 right click = 3
                    pos = pygame.mouse.get_pos()
                    
                    if pos[1] <= barHeight:
                        self.reset()
                    else:
                        #convert real coordinates to grid corrdinates
                        row = (pos[1] - barHeight) // (tileWidth + border)
                        column = pos[0] // (tileWidth + border)
                        #solve issue where you can click outsie of grid range
                        if row >= gridHeight:
                            row = gridHeight-1
                        if column >= gridWidth:
                            column = gridWidth-1
                        
#                        to detect both left and right detect 2 held down then trigger when one releases
                        if 1 in keysDown and 3 in keysDown:
                            if button == 1 or button == 3:
                                self.middle_click(row, column)
                        elif button == 2:
                            self.middle_click(row, column)
                        elif button == 1:
                            self.left_click(row, column)
                        elif button ==3:
                            self.right_click(row, column)
                    
                    if button in keysDown:   
                            del keysDown[button]
                            
            self.render()
            pygame.display.update()
            clock.tick(fps) #frames per second
        
        pygame.quit()
        quit()
        
if __name__ == '__main__':     
    Game()