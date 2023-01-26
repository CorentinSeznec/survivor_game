
import pygame
import math


class Player:
    def __init__(self, wideRange=40, lengthRange = 100):
        self.x = 820
        self.y = 480
        self.health = 100
        self.speed = 1.75
        self.dir_x = -1 # 1 ou -1
        self.dir_y = 0
        self.angleOrientation = 180
        self.lenOrientationVector = 8
        self.radius = 5
        self.wideRange = wideRange
        self.lengthRange = lengthRange
        
    def _angleToOrientVector(self, angle, length = None):
        if length is None:
            length = self.lenOrientationVector
        x, y = self._angleToVector(angle)
        return (x * length, y * length) 

    def _angleToVector(self, angle):
        return (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
    
    def drawMe(self, screen):
        color = (0, 255, 0)
        pygame.draw.circle(screen, color = color, center = (self.x, self.y), radius = self.radius, width = 2) 
        # petite barre de l'agent
        orientation = self._angleToOrientVector(self.angleOrientation) 
        pygame.draw.line(screen, (10,10,80), (self.x, self.y), 
                (self.x+orientation[0], self.y + orientation[1]),1)
        pass
    
    ### ADDED FROM THE ORIGINAL CODE
    def input(self):

        keys = pygame.key.get_pressed()

        # movement input
        if keys[pygame.K_UP]:
            self.dir_y = -1
            self.angleOrientation = 90
         
        elif keys[pygame.K_DOWN]:
            self.dir_y = 1
            self.angleOrientation = 270
    
        else:
            self.dir_y = 0

        if keys[pygame.K_RIGHT]:
            self.dir_x  = 1
            self.angleOrientation = 0

        elif keys[pygame.K_LEFT]:
            self.dir_x  = -1
            self.angleOrientation =  180

        else:
            self.dir_x  = 0
      
