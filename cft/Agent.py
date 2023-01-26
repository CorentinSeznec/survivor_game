import pygame
import math
import random

### ADDED FROM THE ORIGINAL CODE
class Agent:
    def __init__(self,x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.count =0
        if team ==1:
            self.speed = 1
            self.angleSpeed = 2   # turning speed
            self.wideRange = 70     #  wide sight
            self.lengthRange = 60 # length of sight
            
        if team ==2: # gray
            self.speed = 1.3
            self.angleSpeed = 2   # turning speed
            self.wideRange = 40     #  wide sight
            self.lengthRange = 70 # length of sight
        
        if team ==3: # yellow
            self.speed = 0.25
            self.angleSpeed = 1   # turning speed
            self.wideRange = 90     #  wide sight
            self.lengthRange = 150 # length of sight
        
        if team ==4: # pink
            self.speed = 0.25
            self.angleSpeed = 0.5   # turning speed
            self.wideRange = 20     #  wide sight
            self.lengthRange = 40 # length of sight
        
        directions = [1,-1]
        self.dir_x = random.choice(directions) 
        self.dir_y = random.choice(directions) 
        self.angleOrientation = random.randint(0, 359) # de 0 à 359 
        
        self.orientation1 = []
        self.orientation2 = []
        self.raylist = []
        

        self.radius = 10 # radius of circle 
        self.lenOrientationVector = 20

        self.inSight = 0
        self.chasing = 0
        
        self.last_position_player = []
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
            elif self.team == 2:
                color = (48,48,48)#
            elif self.team == 3:
                color = (255, 203, 96)
            elif self.team == 4:
                color = (250,200, 200)
    
     
        pygame.draw.circle(screen, color = color, center = (self.x, self.y), radius = self.radius, width = 3) 
    
        pygame.draw.circle(screen, color = (0,0,0), center = (self.x, self.y), radius = 25, width = 2) 
        

        for i in range(0, len(self.raylist), 2):

            
            orientation1 = self._angleToOrientVector(self.raylist[i][0] + self.angleOrientation - self.wideRange, self.raylist[i][1] )
            orientation1 = (self.x+orientation1[0], self.y+orientation1[1])
            orientation2 = self._angleToOrientVector(self.raylist[i+1][0] + self.angleOrientation - self.wideRange,self.raylist[i+1][1] )
            orientation2 = (self.x+orientation2[0], self.y+orientation2[1])
 
            pygame.draw.polygon(screen, color, [(self.x,self.y), orientation1, orientation2])
        
        
        # petite barre de l'agent
        orientation = self._angleToOrientVector(self.angleOrientation) 
        pygame.draw.line(screen, (10,10,80), (self.x, self.y), 
                (self.x+orientation[0], self.y + orientation[1]),2)
        

    def selectDirection(self, dst_x, dst_y, _grid, __cellSize__):
        # if obstacles
        if _grid._grid.item(dst_x, dst_y):
            
            directions = [self.dir_x, self.dir_y]
            is_free_path_x_y = [1, 1]
            
            # diagonale
            if all(directions) in [-1,1] :
                
                #check if there is a block next to the obstacle
                if _grid._grid.item((int((self.x+directions[0])/__cellSize__), int(self.y/__cellSize__))):
                    #obstacle 
                    is_free_path_x_y[0] = 0
                    
                if _grid._grid.item((int(self.x/__cellSize__), int((self.y+directions[1])/__cellSize__))):
                    #obstacle
                    is_free_path_x_y[1] = 0
                    

                if all(is_free_path_x_y):
        
                    
                    random_dir = [1, 2, 3] 
                
        
                    if _grid._grid.item((int((self.x+directions[0])/__cellSize__), int((self.y-directions[1])/__cellSize__))):# or outside_map_x(a.x+directions[0]) or outside_map_y(a.y-directions[1]):
                        #obstacle
                        random_dir[1] = 0
                    if _grid._grid.item((int((self.x-directions[0])/__cellSize__), int((self.y+directions[1])/__cellSize__))):# or outside_map_x(a.x-directions[0]) or outside_map_y(a.y+directions[1]):
                        #obstacle
                        random_dir[2] = 0
                
                    
                    random_dir  = [random_dir[i] for i in range(3) if random_dir[i] != 1]

                    selected_dir = random.choice(random_dir)
                    
                    if selected_dir == 1:
                        self.dir_x = -1*self.dir_x
                        self.dir_y = -1*self.dir_y
                    elif selected_dir == 2:
                        self.dir_y = -1*self.dir_y
                    else :
                        self.dir_x = -1*self.dir_x
                    
                    
                
                elif sum(is_free_path_x_y) == 1:
        
                    
                    if is_free_path_x_y[0] == 0:
                        self.dir_x = -1*self.dir_x
                    else:
                        self.dir_y = -1*self.dir_y
                    # partir coté opposé

                else:
        
                    # revient d'ou il vient
                    self.dir_x = -1*self.dir_x
                    self.dir_y = -1*self.dir_y
            
            else: # straight direction
                self.dir_x = -1*self.dir_x
                self.dir_y = -1*self.dir_y
        
 
        pass
