import numpy as np
import time 

def astar(maze, start, end):
    
    a_x, a_y = start
    p_x, p_y = end
    SIZE_X = 12
    SIZE_Y = 12
    
    
    array_f_value_open = np.matrix(np.ones((SIZE_X,SIZE_Y)) * np.inf) # matrix weight unexplored
    array_f_value_close = np.matrix(np.ones((SIZE_X, SIZE_Y)) * np.inf) # matrix wright explored
    array_g_value = np.zeros((SIZE_X,SIZE_Y), dtype = np.int8) # contain distance from the inital
    array_h_value = np.zeros((SIZE_X,SIZE_Y), dtype = np.int8) # matrix distance until the end
    array_parent  =  np.zeros((SIZE_X,SIZE_Y,2)) # matrix of parents

    array_f_value_open[a_x, a_y] = abs(a_x - p_x)+ abs(a_y - p_y)
    current_pos = start
    
    not_finished = True
    # loop until reach the end 

    while not_finished:
        
        # find new position 
        a_x, a_y = int(current_pos[0]), int(current_pos[1]) 
        g_value = array_g_value[a_x][a_y]
        new_g_value = g_value+1
      
        # print("\n\nwhile", current_pos)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            
            # Get node position
            new_a_x, new_a_y = (a_x + new_position[0], a_y + new_position[1])
            new_a_x, new_a_y = new_a_x, new_a_y
            
            # print("\ntesting", new_a_x, new_a_y)
            # Make sure within range
            if new_a_x > SIZE_X - 1 or new_a_x < 0 or new_a_y > SIZE_Y - 1 or new_a_y < 0:
                continue

            # Make sure walkable terrain
            # if maze.item(new_a_x, new_a_y) != 0:
            if maze[new_a_x][new_a_y] != 0:
                continue
            
            if array_f_value_close[new_a_x, new_a_y] != np.inf:
                continue
            
            
            h_value = abs(new_a_x-p_x)+ abs(new_a_y-p_y)
            
            if array_f_value_open[new_a_x, new_a_y] != np.inf:
                if array_g_value[new_a_x][new_a_y] > new_g_value:
                    # print("This neighboor is already in the open list, but better way")
                    array_g_value[new_a_x][new_a_y] = new_g_value
                    array_f_value_open[new_a_x, new_a_y] = new_g_value + h_value
                    array_parent[new_a_x][new_a_y][:] = a_x, a_y
                
                
                else:
                    # print("This neighboor is already in the open list, not a better way")
                    continue
            else:
                array_h_value[new_a_x][new_a_y] = h_value
                array_g_value[new_a_x][new_a_y] = new_g_value
                f_value = new_g_value + h_value
                array_f_value_open[new_a_x, new_a_y] = f_value
                array_parent[new_a_x][new_a_y][:] = a_x, a_y
                
        
        # update the explored positions
        array_f_value_close[a_x, a_y] = array_f_value_open[a_x, a_y]
        array_f_value_open[a_x, a_y] = np.inf
        
        # stop if end is reached
        if current_pos == [p_x, p_y] or np.min(array_f_value_open) == np.inf:
            not_finished = False
            
        # updating current position to the minimal weight
        min_array = np.where(array_f_value_open == array_f_value_open.min())
        min_distance_from_end = np.inf
        idx = 0
        
        for _idx, pos in enumerate(zip(min_array[0][:], min_array[1][:])):
            if array_h_value[pos[0], pos[1]] < min_distance_from_end:
                idx = _idx
                min_distance_from_end = array_h_value[pos[0], pos[1]]
            
        current_pos = min_array[0][idx], min_array[1][idx]
    
    
    
    current_pos = end
    path = []

    while current_pos[0] != start[0] or current_pos[1] != start[1]:
        current_pos = int(current_pos[0]), int(current_pos[1])
        path.append(current_pos)
        current_pos = array_parent[current_pos[0]][current_pos[1]]
        
   
     
    return path[::-1]

    
        
def main():

 

    maze = [[0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]]

    start = (0, 0)
    end = (11, 11)

    start_t = time.time()
    path = astar(maze, start, end)
    end_t = time.time()
    print("time:", end_t-start_t)


if __name__ == '__main__':
    main()