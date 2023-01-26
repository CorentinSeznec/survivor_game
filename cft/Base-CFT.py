import sys, math, random
import os.path as path
import pygame
import pygame.draw
import numpy as np
import time


from Explosion import Explosion
from Agent import Agent
from Player import Player
import Astar as astar

# Global variable that may be changed when loading maze
__screenSize__ = (2000,1200)
__cellSize__ = 10
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __screenSize__))

__defaultMazeSize__ = (90, 50) # number of tile on map

__colors__ = [(255, 255, 255), (0, 0, 0), (180, 180, 180), (30, 30, 30), (100, 10, 10)]

def getColorCell(n):
    assert n < len(__colors__)
    return __colors__[n] 

class Grid:
    print("Grid,__screenSize__ ", __screenSize__)

    _grid = None

    def __init__(self, mazename = None):
        if mazename is None:
            self._grid = np.empty(__defaultMazeSize__, dtype='int8')
        else:
            self.loadTextMaze(mazename)
            print("Creating a grid of dimensions", self._grid.shape)

    def loadTextMaze(self, f):
        values = {'.':0,'X':1,'x':2, 's':11, 'S':12, 'f':21, "F":22}
        ls = []
        with open(f,"r") as fin:
            size = tuple([int(x) for x in fin.readline().rstrip().split(' ')])
            print("Reading Midimaze file of size", size)
            for s in fin:
                ls.append([values[x] for x in s.rstrip()])
            matrix = np.array(ls, dtype='int8')
        matrix = np.rot90(np.fliplr(matrix))
        self._grid = matrix 

    def saveTextMaze(self, f):
        values = {0:".", 1:"X", 2:"x", 11:"s", 12:"S", 21:"f", 22:"F"}
        d = self._grid.shape
        with open(f,"w") as fout:
            print(d[0], d[1], file=fout)
            print("Saving Midimaze-like file",f)
            for y in range(d[1]):
                for x in range(d[0]):
                    print(values[self._grid[x,y]], end="", file=fout)
                print(file=fout)

    def addWallFromMouse(self, coord, w):
        x = int(coord[0] / __cellSize__)
        y = int(coord[1] / __cellSize__)
        self._grid[x,y] = w
        self._grid[self._grid.shape[0]-x-1,self._grid.shape[1]-y-1] = w

    def loadGrid(self, grid):
        assert len(grid) == len(self._grid)
        self._grid = np.flipud(np.array(grid, dtype='int8'))

    def drawMe(self):
        pass



class Assets:
    def __init__(self):
        global __cellSize__ 
        self.explosionAnim = []
        img_dir = "."
        for i in range(9):
            filename = './assets/regularExplosion0{}.png'.format(i)
            print(filename)
            img = pygame.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey((0,0,0))
            img = pygame.transform.scale(img, (__cellSize__ * 3, __cellSize__ * 3))
            self.explosionAnim.append(img)



class Scene:
    _mouseCoords = (0,0)
    _grid = None
    _font = None
    _drawGrid = False
    allsprites = pygame.sprite.Group()

    def __init__(self, mazename = None):
        global __screenSize__, __gridDim__
        pygame.init()
        self._grid = Grid(mazename)
        __screenSize__ = tuple(s * __cellSize__ for s in self._grid._grid.shape)
        __gridDim__ = self._grid._grid.shape
        self._screen = pygame.display.set_mode(__screenSize__)
        self.assets = Assets()
        self._font = pygame.font.SysFont('Arial',25)
        self.agents = [Agent(700, 250, 3), Agent(400, 150, 2), Agent(200, 40, 4), Agent(500, 300, 1)]
        self.player = Player()


    ### ADDED FROM THE ORIGINAL CODE
    def outside_map_x(self, dst_x):
        return 1 if dst_x >= int(__screenSize__[0]/__cellSize__) or dst_x <= 0 else 0
    
    ### ADDED FROM THE ORIGINAL CODE
    def outside_map_y(self, dst_y):
        return 1 if dst_y >= int(__screenSize__[1]/__cellSize__) or dst_y <= 0 else 0
    
    ### ADDED FROM THE ORIGINAL CODE
    def movePlayer(self):
    
        # destination, next tile
        dst_x = int((self.player.x + self.player.speed * self.player.dir_x) / __cellSize__)
        dst_y = int((self.player.y + self.player.speed * self.player.dir_y) / __cellSize__)
        
        # check if not outside the map or a wall
        def wall(dst_x, dst_y):
            return 1 if self._grid._grid.item(int(dst_x), int(dst_y)) else 0

        dst_x_is_out = self.outside_map_x(dst_x)
        dst_y_is_out = self.outside_map_y(dst_y)
        
        if not dst_x_is_out and not dst_y_is_out:
            is_wall = wall(dst_x, dst_y)
            if not is_wall:
                # set the new position
                self.player.x += self.player.speed * self.player.dir_x
                self.player.y += self.player.speed * self.player.dir_y
                
                
    ### ADDED FROM THE ORIGINAL CODE           
    def moveAgents(self):
        
        # movement & angle
        nextTileMovement = { (0,-1): 90, (1,0): 0,  (1,-1): 45, (-1, -1): 135, (-1, 0): 180,  (-1, 1): 225, (0,1): 270, (0,0): 270, (1,1): 315, }
        
        for a in self.agents: 
            # the player has been seen, move toward his last known position
            if a.chasing:
                # follow A* direction
                x_player, y_player = a.last_position_player 
                # the player is still in sight
                if a.inSight:
                    # compute A*
                    a.path = astar.astar(self._grid._grid, (int(a.x/__cellSize__), int(a.y/__cellSize__)), (x_player, y_player))
                    a.path.pop(0)
                    # special comportment for agent 4 (pink)
                    if a.team == 4:
                        a.speed = 1.5
                        a.wideRange = 80     
                        a.lengthRange = 80
                
                if len(a.path) == 0:
                    print("I LOST HIM, BECAREFUL HE IS NOT FAR")
                    a.chasing = 0
                    a.inSight = 0
                    continue
                    
                # get the position from the A* list
                a.next_pos_x, a.next_pos_y = a.path[0][0], a.path[0][1] 
                curr_pos_normalized_x = int(a.x/__cellSize__)
                curr_pos_normalized_y = int(a.y/__cellSize__)
                # Define direction in x and y
                a.dir_x = 1 if a.next_pos_x > curr_pos_normalized_x else 0 if a.next_pos_x ==curr_pos_normalized_x else -1
                a.dir_y = 1 if a.next_pos_y > curr_pos_normalized_y else 0 if a.next_pos_y == curr_pos_normalized_y else -1
                a.x = a.x + a.speed * a.dir_x
                a.y = a.y + a.speed * a.dir_y
                # when the player reached the nex pos, withdraw the position from the A* list
                if int(a.x/__cellSize__) == a.next_pos_x and int(a.y/__cellSize__) == a.next_pos_y :
                    a.path.pop(0)
                # from the direction, conversion into an angle
                a.angleOrientation  = nextTileMovement.get((a.dir_x,a.dir_y))
                
            # Not seen the player, random move   
            else:
               
                if a.team == 4:
                    a.speed = 0.5
                    a.angleSpeed = 0.5   # turning speed
                    a.wideRange = 30     #  wide sight
                    a.lengthRange = 50 # length of sight
                    
                # sometimes, make a random move to break linearity
                if random.random() < 0.015:
                    new_dir = [1, -1]
                    a.dir_x = random.choice(new_dir)
                    a.dir_y = random.choice(new_dir)
                
                dst_x = int( (a.x + a.speed * a.dir_x)/__cellSize__)
                dst_y = int((a.y + a.speed * a.dir_y) /__cellSize__)
        
                # check if not outside the map
                dst_x_is_out = self.outside_map_x(dst_x)
                dst_y_is_out = self.outside_map_y(dst_y)
                
                #considérer les bords comme un mur
                if not (dst_x_is_out or dst_y_is_out):
                    a.selectDirection(dst_x, dst_y, self._grid, __cellSize__)
                            
                else: # outside the map
                    if dst_x_is_out:
                        a.dir_x = -1*a.dir_x
                    else:
                        a.dir_y = -1*a.dir_y
                    
                
                a.x += a.speed * a.dir_x
                a.y += a.speed * a.dir_y
                a.angleOrientation += a.angleSpeed
                if a.angleOrientation > 359:
                    a.angleOrientation = 0
                pass
      
            
    ### ADDED FROM THE ORIGINAL CODE
    def update_sightAgent(self):
        
        for a in self.agents:
            # find the left and right angle for the visionSight
            leftAngle = a.angleOrientation-a.wideRange
            rightAngle = a.angleOrientation+a.wideRange
            
            # list for the index and the range of the raycast
            a.raylist.clear()
            
            # position of the  agent
            x1 = int((a.x)/__cellSize__)
            y1 = int((a.y)/__cellSize__)
            
            last_dist =  -1
            yet_detected = 0
            
            # for each ray in the visionSight
            for index, angleray in enumerate(np.arange(leftAngle,rightAngle,1)):
                
                # get a ray from the angle and the  max distance
                ray = a._angleToOrientVector(angleray, a.lengthRange)
                # find the limit of the ray
                x2 = int((a.x+ray[0])/__cellSize__)
                y2 = int((a.y+ray[1])/__cellSize__)
                # limit the ray inside the map
                x2 = int(__screenSize__[0]/__cellSize__)-1 if self.outside_map_x(x2) else x2
                y2 = int(__screenSize__[1]/__cellSize__)-1 if self.outside_map_y(y2) else y2   
                # return the  position of the player and the position of the obstacle if finded else 0
                pos_player, pos_obstacle = self.firstObstacle(x1, y1, x2, y2)
                
                # get the max distance
                if pos_obstacle:
                    dist = (pos_obstacle[0] - x1)**2 +(pos_obstacle[1] - y1)**2
                else:
                    dist = a.lengthRange
                
                # this ray is the first to detect the player
                if pos_player and not yet_detected:
                    print("INTRUDER DETECTED!!!")
                    a.chasing = 1
                    a.inSight = 1
                    a.last_position_player = pos_player
                    yet_detected = 1
                 
                # adapt the visionSight to obstacle       
                if last_dist != dist:
                    if index != 0:
                        a.raylist.append((index-1, last_dist))
                    a.raylist.append((index, dist))
                last_dist = dist 
            # add the last index
            a.raylist.append((index, dist)) 
            
            
        
            player_x, player_y = int(self.player.x/__cellSize__), int(self.player.y/__cellSize__)
            distance = int(math.sqrt((player_x-x1)**2 + (player_y-y1)**2))
            
            if distance <2.5 and not yet_detected:
                
                a.chasing = 1
                a.inSight = 1
                a.last_position_player = player_x, player_y
                yet_detected = 1
            
            # if no ray detect the player, no detection in this visionSight
            if not yet_detected:
                a.inSight = 0
            
            pass
     
            
            

    def drawMe(self):
        if self._grid._grid is None:
            return
        if self._drawGrid:
            self._screen.fill((128,128,128))
        else:
            self._screen.fill((255,255,255))

        for agent in self.agents:
            agent.drawMe(self._screen)
        
        self.player.drawMe(self._screen)

        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):


                if self._drawGrid:
                    pygame.draw.rect(self._screen, 
                        (getColorCell(self._grid._grid.item((x,y)))),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))
                
                elif self._grid._grid.item(x,y) != 0:
                    # draw wall and obstacle if no grid
                    pygame.draw.rect(self._screen, 
                        (getColorCell(self._grid._grid.item((x,y)))),
                        (x*__cellSize__ , y*__cellSize__, __cellSize__, __cellSize__))

        self.allsprites.draw(self._screen)

    def drawText(self, text, position, color = (255,64,64)):
        self._screen.blit(self._font.render(text,1,color),position)

    def _mapOnPath(self, x1, y1, x2, y2, fmap):  
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x_player = int(self.player.x/__cellSize__)
        y_player = int(self.player.y/__cellSize__)

        xincr = 1 if x1 < x2 else -1
        yincr = 1 if y1 < y2 else -1
     
        seen_player = 0
        x = x1; y = y1
        if (dx > dy):
            e = dx // 2
            for i in range(dx):
                x += xincr; e += dy
                
                if e > dx:
                    e -= dx; y += yincr
                
                if (x,y) == (x_player,y_player):
                    seen_player = (x,y)
                    
              
                if (retIfNotNone := fmap(x,y)) :
                    
                    return seen_player, retIfNotNone
     
            return seen_player, 0
    
        else:
            e = dy // 2
            for i in range(dy):
                y += yincr; e += dx
                if e > dy:
                    e -= dy; x += xincr
                
                if (x,y) == (x_player,y_player):
                    seen_player = (x,y)
                    
    
                if (retIfNotNone := fmap(x,y)) :
                    
                    return seen_player, retIfNotNone

            return seen_player, 0
        print("issue")
        return (0,0)


        
        
        
    def canSee(self, x1, y1, x2, y2, fog = 20):
        
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # 1) Checks the distance
        manhattanDistance = abs(x1 - x2) + abs(y1 - y2)
        if manhattanDistance > fog:
            return False

        # 2) Checks the angles (NPC cannot see other players outside of their vision) TODO

        # 3) Checks on the tiles (Brensenham)
        _mapLevel = lambda x, y : True if self._grid._grid[x, y] == 1 else None
       
        
        return self._mapOnPath(x1, y1, x2, y2, _mapLevel)

    ### ADDED FROM THE ORIGINAL CODE
    # O if there is no wall on the path, otherwise gives the first wall coordinates
    def firstObstacle(self, x1, y1, x2, y2):

        x2 = __screenSize__[0]-2 if self.outside_map_x(x2) else x2
        y2 = __screenSize__[1]-2 if self.outside_map_y(y2) else y2
        _mapLevel = lambda x, y : (x,y) if self._grid._grid[x, y] == 1 else 0
        return self._mapOnPath(x1, y1, x2, y2, _mapLevel) 

    def update(self):
        
        self.update_sightAgent()
        self.moveAgents()
        self.player.input()
        self.movePlayer()
        self.allsprites.update()
        

    def eventClic(self,coord,b): # ICI METTRE UN A* EN TEMPS REEL
        pass

    def recordMouseMove(self, coord):
        pass

def main():
    #_, grid = loadmidimazefile("mazes/WS32.MAZ")
    buildingGrid = False #True if the user can add / remove walls / weights
    scene = Scene()#Scene("mazes/WS32-bis.MAZ")
    scene._grid.loadTextMaze("maze_difficult.maz")

    # position at the start
    x1 = __screenSize__[0]/3/__cellSize__
    y1 = __screenSize__[1]/2/__cellSize__

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
        checksee = scene.canSee(x1, y1, x2, y2)

        additionalMessage += " CAN-SEE" if checksee else " CANNOT-SEE"
        
        # Draw the first obstacle on the path
        color_ray_valid = (255,60,60)
        color_ray_invalid = (60, 255, 60)
        pygame.draw.line(scene._screen, color_ray_valid if checksee else color_ray_invalid,  (x1*__cellSize__, y1 *__cellSize__), pygame.mouse.get_pos())
        # if (obstacle := scene.firstObstacle(x1, y1, x2, y2))[1] is not None:
        #     ox, oy = obstacle[1]
        #     pygame.draw.rect(scene._screen, (200,100,100), 
        #         (ox*__cellSize__ , oy*__cellSize__, __cellSize__, __cellSize__)) # color of the wall if pointer on it

        # scene.drawText("CFT" + additionalMessage, (10,10))
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

