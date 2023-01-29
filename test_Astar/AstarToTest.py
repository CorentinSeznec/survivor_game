import time 
class Node():

    def __init__(self, parent=None, position=None, direction = (0,0)):
        self.parent = parent
        self.position = position
        self.direction = direction
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end):
    timer_start = time.time()
    # start and end node
    start_node = Node(None, start)
    start_node.g, start_node.h, start_node.f = 0, 0, 0
    end_node = Node(None, end)
    end_node.g, end_node.h, end_node.f = 0, 0, 0

    # I open and closed list
    open_list = []
    closed_list = []
  
    
    # Add the start node
    open_list.append(start_node)
    l = 0
    # Loop until you find the end
    while len(open_list) > 0:
        
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            
            return path[::-1] # Return reversed path

        # Generate children
        children = []
       
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            
            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            
            
            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

         
            # Make sure walkable terrain
       
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position, new_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            already_closed = 0
            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    already_closed = 1
                    continue
            if already_closed:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            already_open = 0
            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    already_open = 1
                    continue
            if already_open:
                continue

            # Add the child to the open list
            open_list.append(child)
        l+=1

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