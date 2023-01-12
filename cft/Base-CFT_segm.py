import sys, math, random
import os.path as path
import pygame
import pygame.draw
import numpy as np

import Grid
from Player import Player
from Agent import Agent
from Assets import Assets
from Scene import Scene
# Global variable that may be changed when loading maze
__screenSize__ = Grid.__screenSize__
__cellSize__ = Grid.__cellSize__
__gridDim__ = Grid.__gridDim__




class Explosion(pygame.sprite.Sprite):
    ''' A simple class to take care of animated explosions by sprites from pygame '''
    def __init__(self, center, anim):
        pygame.sprite.Sprite.__init__(self)
        self.anim = anim
        self.image = self.anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def main():
    #_, grid = loadmidimazefile("mazes/WS32.MAZ")
    buildingGrid = False #True if the user can add / remove walls / weights
    scene = Scene()#Scene("mazes/WS32-bis.MAZ")
    scene._grid.loadTextMaze("maze.maz")

    # position at the start
    x1 = __screenSize__[0]/3/__cellSize__
    y1 = __screenSize__[1]/2/__cellSize__
    print("__cellSize__", __cellSize__)
    print("__screenSize__[0]", __screenSize__[0])
    print("__screenSize__[1]", __screenSize__[1])

    done = False
    clock = pygame.time.Clock()
    wallWeight = 1
    while done == False:
        clock.tick(20)
        scene.update()
        scene.drawMe()
        if buildingGrid:
            additionalMessage = ": BUILDING (" + str(int(wallWeight*100)) + "%)"
        else:
            additionalMessage = ""

        x2 = pygame.mouse.get_pos()[0]/__cellSize__
        y2 = pygame.mouse.get_pos()[1]/__cellSize__
        print("llaaaa", x1, y1)
        print("llaaaa", x2, y2)
        checksee = scene.canSee(x1, y1, x2, y2)

        additionalMessage += " CAN-SEE" if checksee else " CANNOT-SEE"
        
        # Draw the first obstacle on the path
        color_ray_valid = (255,60,60)
        color_ray_invalid = (60, 255, 60)
        pygame.draw.line(scene._screen, color_ray_valid if checksee else color_ray_invalid,  (x1*__cellSize__, y1 *__cellSize__), pygame.mouse.get_pos())
        if (obstacle := scene.firstObstacle(x1, y1, x2, y2)) is not None:
            ox, oy = obstacle
            pygame.draw.rect(scene._screen, (200,100,100), 
                (ox*__cellSize__ , oy*__cellSize__, __cellSize__, __cellSize__)) # color of the wall if pointer on it

        scene.drawText("CFT" + additionalMessage, (10,10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True
            if event.type == pygame.KEYDOWN: 
                print(event.unicode)
                if event.unicode in ["0", "1", "2"]:
                    wallWeight = int(event.unicode) 
                    break
                if event.key == pygame.K_q or event.key==pygame.K_ESCAPE: # q
                    print("Exiting")
                    done = True
                    break
                if event.key == pygame.K_s: # s
                    np.save("matrix.npy",scene._grid._grid)
                    print("matrix.npy saved")
                    break
                if event.key == pygame.K_l: # l
                    print("matrix.npy loaded")
                    scene._grid._grid = np.load("matrix.npy")
                    scene._grid.saveTextMaze("maze.maz")
                    break
                if event.key == pygame.K_n:
                    buildingGrid = False
                    break
                if event.key == pygame.K_b :
                    buildingGrid = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buildingGrid:
                    scene._grid.addWallFromMouse(event.dict['pos'], wallWeight)
                else:
                    scene.eventClic(event.dict['pos'],event.dict['button'])
                    # Add an explosion (just to show how to do that)
                    scene.allsprites.add(Explosion(event.dict['pos'], scene.assets.explosionAnim))
                    x1, y1 = event.dict['pos'][0]/__cellSize__, event.dict['pos'][1] / __cellSize__

            elif event.type == pygame.MOUSEMOTION:
                scene.recordMouseMove(event.dict['pos'])

    pygame.quit()

if not sys.flags.interactive: 
    main()

