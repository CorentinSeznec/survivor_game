import sys, math, random
import os.path as path
import pygame
import pygame.draw
import numpy as np

from Explosion import Explosion
from Agent import Agent
from Player import Player
import Astar

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
        self.agents = [Agent(1, angleSpeed = 2, wideRange = 40, lengthRange = 120), Agent(2, angleSpeed = 1, wideRange = 50, lengthRange = 100), Agent(1, angleSpeed =0.8, wideRange= 130, lengthRange = 140)]
        self.player = Player()
        self.agents[0].x = 700
        self.agents[0].y = 250
        self.agents[0].speed = 4

        self.agents[1].x = 200
        self.agents[1].y = 30
        
 
        self.agents[2].x = 400
        self.agents[2].y = 400
        


    # speed
    def update_sightAgent(self):
        X_MAX, Y_MAX = __screenSize__
        for a in self.agents:
            if a.team == 1:
                color = (200,200,250)
            else:
                color = (250,200, 200)
            
            # envoi des rays:

            pgauche = a.angleOrientation-a.wideRange
            pdroite = a.angleOrientation+a.wideRange
        
            a.raylist = []
            x1 = int((a.x)/__cellSize__)
            y1 = int((a.y)/__cellSize__)
            last_dist =  -1
            dist = -1
            seen_player = 0
            detected = 0
            for index, angleray in enumerate(np.arange(pgauche,pdroite,1)):
                
                ray = a._angleToOrientVector(angleray, a.lengthRange)
        
                x2 = int((a.x+ray[0])/__cellSize__)
                y2 = int((a.y+ray[1])/__cellSize__)
                if x2>= X_MAX: 
                    x2 = X_MAX-1
                    
                if y2>= Y_MAX:
                    y2 = Y_MAX-1
                
                # obstacle
                pos_player_n_obstacle = self.firstObstacle(x1, y1, x2, y2)
                pos_player, pos_obstacle = pos_player_n_obstacle[0], pos_player_n_obstacle[1]
                
                    
                if pos_obstacle:
                    dist = (pos_obstacle[0] - x1)**2 +(pos_obstacle[1] - y1)**2
                else:
                    dist = a.lengthRange
                
       
                if pos_player and not detected:
                    a.chasing = 1
                    a.inSight = 1
                    a.last_position_player = pos_player
                    detected = 1
                    # a.color = (255, 0,0)
                
                
                
                if last_dist != dist:
                    if index != 0:
                        a.raylist.append((index-1, last_dist))
                    a.raylist.append((index, dist))
                last_dist = dist
                
            # add last index
                if not detected:
                    a.inSight = 0
                    
            a.raylist.append((index, dist)) 


       
         
                    
            
            
            
    def moveAgents(self):
 
        X_MAX, Y_MAX = __screenSize__

        
        
        for a in self.agents:  
            
            if a.chasing:
                
               
                # follow A*
                 # rajouter les conditions ppur plus de sécurité
                # if a.inSight:
                    print("IN SIGHT")
                    x_player, y_player = a.last_position_player 
                    # A*
                    
                    self.path = Astar.astar(self._grid._grid, (int(a.x/__cellSize__), int(a.y/__cellSize__)), (x_player, y_player))
                    self.path.pop(0)
                 
                    a.dir_x = self.path[0][0] 
                    a.dir_y = self.path[0][1] 
                    a.x = a.x + a.speed * a.dir_x
                    a.y = a.y + a.speed * a.dir_y
                    print("self.path", self.path)
                    self.path.pop(0)
                 
                    if len(self.path) == 0:
                        print("REACH")
                        a.chasing = 0
                        a.inSight = 0
                        
                    
                # else:
                #     print("NOT IN SIGHT")
                #     a.dir_x = self.path[0][0] 
                #     a.dir_y = self.path[0][1] 
                #     print("self.path", self.path)
                #     a.x = a.x + a.speed * a.dir_x
                #     a.y = a.y + a.speed * a.dir_y
                    
                #     self.path.pop(0)
                #     if len(self.path) == 0:
                #         print("REACH")
                #         a.chasing = 0
                #         a.inSight = 0
                      
            else:
                
                # destination
                dst_x = a.x + a.speed * a.dir_x
                dst_y = a.y + a.speed * a.dir_y
        
                # check if not outside the map
                def outside_map_x(dst_x):
                    if dst_x >= X_MAX or dst_x <= 0:
                        return 1
                    else: 
                        return 0
                def outside_map_y(dst_y):
                    if dst_y >= Y_MAX or dst_y <= 0:
                        return 1
                    else: 
                        return 0

                dst_x_is_out = outside_map_x(dst_x)
                dst_y_is_out = outside_map_y(dst_y)
                
                #considérer les bords comme un mur
                if not (dst_x_is_out or dst_y_is_out):
                    # if obstacles
                    if self._grid._grid.item((int(dst_x/__cellSize__), int(dst_y/__cellSize__))):
                        
                        directions = [a.dir_x, a.dir_y]
                        is_free_path_x_y = [1, 1]
                        
                        # diagonale
                        if all(directions) in [-1,1] :
                            
                            #check if there is a block next to the obstacle
                            if self._grid._grid.item((int((a.x+directions[0])/__cellSize__), int(a.y/__cellSize__))):# or outside_map_x(a.x+directions[0]) or outside_map_y(a.y+directions[1]) :
                                #obstacle 
                                is_free_path_x_y[0] = 0
                                
                            if self._grid._grid.item((int(a.x/__cellSize__), int((a.y+directions[1])/__cellSize__))):# or outside_map_x(a.x+directions[0]) or outside_map_y(a.y+directions[1]):
                                #obstacle
                                is_free_path_x_y[1] = 0
                                

                            if all(is_free_path_x_y):
                    
                                
                                random_dir = [1, 2, 3] 
                            
                                
                                if self._grid._grid.item((int((a.x+directions[0])/__cellSize__), int((a.y-directions[1])/__cellSize__))):# or outside_map_x(a.x+directions[0]) or outside_map_y(a.y-directions[1]):
                                    #obstacle
                                    random_dir[1] = 0
                                if self._grid._grid.item((int((a.x-directions[0])/__cellSize__), int((a.y+directions[1])/__cellSize__))):# or outside_map_x(a.x-directions[0]) or outside_map_y(a.y+directions[1]):
                                    #obstacle
                                    random_dir[2] = 0
                            
                                
                                random_dir  = [random_dir[i] for i in range(3) if random_dir[i] != 1]
            
                                selected_dir = random.choice(random_dir)
                                
                                if selected_dir == 1:
                                    a.dir_x = -1*a.dir_x
                                    a.dir_y = -1*a.dir_y
                                elif selected_dir == 2:
                                    a.dir_y = -1*a.dir_y
                                else :
                                    a.dir_x = -1*a.dir_x
                                
                                
                            
                            elif sum(is_free_path_x_y) == 1:
                    
                                
                                if is_free_path_x_y[0] == 0:
                                    a.dir_x = -1*a.dir_x
                                else:
                                    a.dir_y = -1*a.dir_y
                                # partir coté opposé

                            else:
                    
                                # revient d'ou il vient
                                a.dir_x = -1*a.dir_x
                                a.dir_y = -1*a.dir_y
                        
                        else: # straight direction
                            a.dir_x = -1*a.dir_x
                            a.dir_y = -1*a.dir_y
                            
                else: # outside the map
                    if dst_x_is_out:
                        a.dir_x = -1*a.dir_x
                    else:
                        a.dir_y = -1*a.dir_y
                    

                a.x += a.speed * a.dir_x
                a.y += a.speed * a.dir_y
            
            
    def movePlayer(self):
    
        X_MAX, Y_MAX = __screenSize__

        # destination
        dst_x = self.player.x + self.player.speed * self.player.dir_x
        dst_y = self.player.y + self.player.speed * self.player.dir_y
    
        # check if not outside the map
        def outside_map_x(dst_x):
            if dst_x >= X_MAX or dst_x <= 0:
                return 1
            else: 
                return 0
        def outside_map_y(dst_y):
            if dst_y >= Y_MAX or dst_y <= 0:
                return 1
            else: 
                return 0
            
        def wall(dst_x, dst_y):
            if self._grid._grid.item((int(dst_x/__cellSize__), int(dst_y/__cellSize__))):
                return 1
            else:
                return 0

        dst_x_is_out = outside_map_x(dst_x)
        dst_y_is_out = outside_map_y(dst_y)
        
        
        if not dst_x_is_out and not dst_y_is_out:
            is_wall = wall(dst_x, dst_y)
            if not is_wall:
                self.player.x += self.player.speed * self.player.dir_x
                self.player.y += self.player.speed * self.player.dir_y
        

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

    # None if there is no obstacle on the path, otherwise gives the first obstacle coordinates
    def firstObstacle(self, x1, y1, x2, y2):
        X_MAX, Y_MAX = __screenSize__ 
        X_MAX, Y_MAX = int(X_MAX/__cellSize__), int(Y_MAX/__cellSize__)
        
        x_player = int(self.player.x/__cellSize__)
        y_player = int(self.player.y/__cellSize__)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        if x2 >= X_MAX:
            x2 = X_MAX -2
        if y2 >= Y_MAX:
            y2 = Y_MAX -2
        
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
    scene._grid.loadTextMaze("maze.maz")

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

