import pygame
import math

class Agent:
    def __init__(self, team,chasing = 0,angleSpeed = 3, wideRange = 40, lengthRange = 100):
        self.x = 300
        self.y = 300

        self.dir_x = 1 # 1 ou -1
        self.dir_y = 1
        self.speed = 0.5
        
        self.orientation1 = []
        self.orientation2 = []
        self.raylist = []
        
        self.color = None
        self.angleOrientation = 90 # de 0 à 359 

        self.angleSpeed = angleSpeed #turning speed
        self.wideRange = wideRange
        self.lengthRange = lengthRange # length of sight

        self.radius = 11 # radius of circle 
        self.lenOrientationVector = 20

        
        self.team = team
        self.inSight = 0
        self.chasing = chasing
        
        self.path = []

    def _angleToVector(self, angle):
        return (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))

    def _tupleMul(self, t,a):
        return tuple([x * a for x in t])

    def _angleToOrientVector(self, angle, length = None):
        if length is None:
            length = self.lenOrientationVector
        x, y = self._angleToVector(angle)
        return (x * length, y * length) 



    def drawMe(self, screen):

        if self.inSight:
            color = (255, 0, 0)
        elif self.chasing:
            color = (255,128,0)
        else: 
            if self.team == 1:
                color = (200,200,250)
            else:
                color = (250,200, 200)
    
     
        pygame.draw.circle(screen, color = color, center = (self.x, self.y), radius = self.radius, width = 3) 
    
        orientation = self._angleToOrientVector(self.angleOrientation) 
        

    
        for i in range(0, len(self.raylist), 2):

            
            orientation1 = self._angleToOrientVector(self.raylist[i][0] + self.angleOrientation - self.wideRange, self.raylist[i][1] )
            orientation1 = (self.x+orientation1[0], self.y+orientation1[1])
            orientation2 = self._angleToOrientVector(self.raylist[i+1][0] + self.angleOrientation - self.wideRange,self.raylist[i+1][1] )
            orientation2 = (self.x+orientation2[0], self.y+orientation2[1])
 
  
            pygame.draw.polygon(screen, color, [(self.x,self.y), orientation1, orientation2])
        
      
     
        
        # 
        # petite barre de l'agent
        pygame.draw.line(screen, (10,10,80), (self.x, self.y), 
                (self.x+orientation[0], self.y + orientation[1]),2)
        
        # print("petite barre", self.x, orientation[0], self.y , orientation[1])
        
        
        self.angleOrientation += self.angleSpeed
        if self.angleOrientation > 359:
            self.angleOrientation = 0
        pass