from pysat.solvers import Glucose3
import random

def read_map(filename):
    """
    Reads the map data from the input file.

    Args:
        filename (str): The name of the input file.

    Returns:
        tuple: A tuple containing the grid size, the map data, and the agent's 
                initial position.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
        grid_size = int(lines[0].strip())
        map_data = [line.strip().split('.') for line in lines[1:]]
        agent_pos = None
        for i in range(grid_size):
            for j in range(grid_size):
                if 'A' in map_data[i][j]: 
                    agent_pos = (i, j)
                break  # Break out of inner loop once agent is found
            if agent_pos:  # Break out of outer loop as well
                break
    return grid_size, map_data, agent_pos

def Breeze(x, y):
    """Returns a unique integer representing the proposition 'There is a breeze at (x, y)'."""
    return (x * 10 + y) * 10 + 1 

def Pit(x, y):
    """Returns a unique integer representing the proposition 'There is a pit at (x, y)'."""
    return (x * 10 + y) * 10 + 2

def Stench(x, y):
    """Returns a unique integer representing the proposition 'There is a stench at (x, y)'."""
    return (x * 10 + y) * 10 + 3

def Wumpus(x, y):
    """Returns a unique integer representing the proposition 'There is a Wumpus at (x, y)'."""
    return (x * 10 + y) * 10 + 4

def Gold(x, y):
    """Returns a unique integer representing the proposition 'There is gold at (x, y)'."""
    return (x * 10 + y) * 10 + 5

def H_P(x, y):
    """Returns a unique integer representing the proposition 'There is a healing potion at (x, y)'."""
    return (x * 10 + y) * 10 + 6

def Glow(x, y):
    """Returns a unique integer representing the proposition 'There is a glow at (x, y)'."""
    return (x * 10 + y) * 10 + 7 

def P_G(x, y):
    """Returns a unique integer representing the proposition 'There is poisonous gas at (x, y)'."""
    return (x * 10 + y) * 10 + 8

def Whiff(x, y):
    """Returns a unique integer representing the proposition 'There is a whiff at (x, y)'."""
    return (x * 10 + y) * 10 + 9

def AdjacentToGold(x, y):
    """Returns a unique integer representing the proposition 'The agent is adjacent to gold at (x, y)'."""
    return (x * 10 + y) * 10 + 10

def create_wumpus_clauses(grid_size):
    """
    Creates the logical clauses for the Wumpus World rules.

    Args:
        grid_size (int): The size of the grid.

    Returns:
        list: A list of clauses representing the Wumpus World rules.
    """
    clauses = []

    # Breeze <-> Pit in adjacent cell
    for x in range(grid_size):
        for y in range(grid_size):
            breeze_clause = [-Breeze(x, y)]
            adjacent_pits = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    adjacent_pits.append(Pit(nx, ny))
                    breeze_clause.append(Pit(nx, ny))
            clauses.append(breeze_clause)
            for pit in adjacent_pits:
                clauses.append([-Pit(nx, ny), Breeze(x, y)])

    # Stench <-> Wumpus in adjacent cell
    for x in range(grid_size):
        for y in range(grid_size):
            stench_clause = [-Stench(x, y)]
            adjacent_wumpus = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    adjacent_wumpus.append(Wumpus(nx, ny))
                    stench_clause.append(Wumpus(nx, ny))
            clauses.append(stench_clause)
            for wumpus in adjacent_wumpus:
                clauses.append([-Wumpus(nx, ny), Stench(x, y)])

    # Whiff <-> Poisonous Gas in adjacent cell
    for x in range(grid_size):
        for y in range(grid_size):
            whiff_clause = [-Whiff(x, y)]
            adjacent_p_g = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    adjacent_p_g.append(P_G(nx, ny))
                    whiff_clause.append(P_G(nx, ny))
            clauses.append(whiff_clause)
            for p_g in adjacent_p_g:
                clauses.append([-P_G(nx, ny), Whiff(x, y)])

    # Glow <-> Healing Potion in adjacent cell
    for x in range(grid_size):
        for y in range(grid_size):
            glow_clause = [-Glow(x, y)]
            adjacent_h_p = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    adjacent_h_p.append(H_P(nx, ny))
                    glow_clause.append(H_P(nx, ny))
            clauses.append(glow_clause)
            for h_p in adjacent_h_p:
                clauses.append([-H_P(nx, ny), Glow(x, y)])

    # At least one Wumpus
    wumpus_clause = []
    for x in range(grid_size):
        for y in range(grid_size):
            wumpus_clause.append(Wumpus(x, y))
    clauses.append(wumpus_clause)

    # At most one Wumpus
    for x1 in range(grid_size):
        for y1 in range(grid_size):
            for x2 in range(grid_size):
                for y2 in range(grid_size):
                    if (x1, y1) != (x2, y2):
                        clauses.append([-Wumpus(x1, y1), -Wumpus(x2, y2)])

    # AdjacentToGold <-> Gold in adjacent cell
    for x in range(grid_size):
        for y in range(grid_size):
            adjacent_gold_clause = [-AdjacentToGold(x, y)]
            adjacent_golds = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    adjacent_golds.append(Gold(nx, ny))
                    adjacent_gold_clause.append(Gold(nx, ny))
            clauses.append(adjacent_gold_clause)
            for gold in adjacent_golds:
                clauses.append([-Gold(nx, ny), AdjacentToGold(x, y)])
    return clauses

def add_initial_percepts(agent_pos, map_data, solver):
    """
    Adds the initial percepts at the agent's starting position to the solver.

    Args:
        agent_pos (tuple): The agent's starting position (x, y).
        map_data (list): The 2D list representing the map.
        solver (Glucose3): The PySAT solver.
    """
    x, y = agent_pos
    cell_content = map_data[x][y]  # Get the content of the starting cell

    if 'B' in cell_content:
        solver.add_clause([Breeze(x, y)])
    elif 'B' not in cell_content:
        solver.add_clause([-Breeze(x, y)])

    if 'P' in cell_content:
        solver.add_clause([Pit(x, y)])
    elif 'P' not in cell_content:
        solver.add_clause([-Pit(x, y)])

    if 'S' in cell_content:
        solver.add_clause([Stench(x, y)])
    elif 'S' not in cell_content:
        solver.add_clause([-Stench(x, y)])

    if 'W' in cell_content:
        solver.add_clause([Wumpus(x, y)])
    elif 'W' not in cell_content:
        solver.add_clause([-Wumpus(x, y)])

    if 'G' in cell_content:
        solver.add_clause([Gold(x, y)])
    elif 'G' not in cell_content:
        solver.add_clause([-Gold(x, y)])

    if 'H_P' in cell_content:
        solver.add_clause([H_P(x, y)])
    elif 'H_P' not in cell_content:
        solver.add_clause([-H_P(x, y)])

    if 'G_L' in cell_content: 
        solver.add_clause([Glow(x, y)])
    elif 'G_L' not in cell_content:
        solver.add_clause([-Glow(x, y)]) 
    
    if 'P_G' in cell_content:
        solver.add_clause([P_G(x, y)])
    else:
        solver.add_clause([-P_G(x, y)])

def is_safe_cell(x, y, solver):
    """
    Checks if a cell is safe to move to based on the current knowledge.

    Args:
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
        solver (Glucose3): The PySAT solver.

    Returns:
        bool: True if the cell is safe, False otherwise.
    """
    if not solver.solve(assumptions=[-Pit(x, y), -Wumpus(x, y)]): # No pit and wumpus
        return True
    else:
        return False

def find_path_to_all_golds(agent_pos, agent_dir, gold_positions, solver, grid_size, map_data):
    """
    Finds a path to collect all the gold in the Wumpus World.

    Args:
        agent_pos (tuple): The agent's starting position (x, y).
        agent_dir (str): The agent's starting direction ('north', 'south', 'east', 'west').
        gold_positions (set): A set of tuples representing the gold positions.
        solver (Glucose3): The PySAT solver.
        grid_size (int): The size of the grid.
        map_data (list): The 2D list representing the map.

    Returns:
        tuple: A tuple containing the path (list of positions) and 
               the actions taken (list of actions).
    """
    path = [agent_pos]
    actions = []
    remaining_gold = set(gold_positions)
    visited = set()  # Keep track of visited cells to avoid loops

    while remaining_gold:
        x, y = agent_pos
        visited.add(agent_pos)

        # Check if the agent is ON the gold before grabbing
        if (x, y) in remaining_gold:
            actions.append('grab')
            print(f"({x}, {y}): grab")  # Print the grab action
            solver.add_clause([-Gold(x, y)])  # No more gold at this location
            solver.add_clause([-AdjacentToGold(x, y)])  # Agent is no longer adjacent to gold here

            remaining_gold.remove((x, y))  # <-- Moved inside the if block
            continue

        # Explore safe adjacent cells
        safe_neighbors = []
        for dx, dy, direction in [(1, 0, 'south'), (-1, 0, 'north'), (0, 1, 'east'), (0, -1, 'west')]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in visited and is_safe_cell(nx, ny, solver):
                safe_neighbors.append((nx, ny, direction))

        if safe_neighbors:
            # Choose a safe neighbor (you can use different strategies here)
            nx, ny, direction = random.choice(safe_neighbors)  # Random choice for now

            # Determine actions to reach the chosen neighbor
            if agent_dir != direction:
                turn_action = 'turn_right' if (agent_dir, direction) in [('north', 'east'), ('east', 'south'), ('south', 'west'), ('west', 'north')] else 'turn_left'
                actions.append(turn_action)
                agent_dir = direction  # Update agent direction
                print(f"({x}, {y}): {turn_action}")  # Print the turn action
            actions.append('move_forward')
            agent_pos = (nx, ny)
            path.append(agent_pos)
            print(f"({x}, {y}): move_forward to ({nx}, {ny})")  # Print the move action
        else:
            if actions and actions[-1] == 'move_forward' and path:
                actions.append('turn_left')  # Turn around (could also use 'turn_right')
                actions.append('turn_left')
                actions.append('move_forward')
                agent_pos = path.pop()  # Remove the current position from the path
                # Recalculate agent direction (reverse of the previous direction)
                if agent_dir == 'north':
                    agent_dir = 'south'
                elif agent_dir == 'south':
                    agent_dir = 'north'
                elif agent_dir == 'east':
                    agent_dir = 'west'
                elif agent_dir == 'west':
                    agent_dir = 'east'
                print(f"({x}, {y}): {turn_action}")  # Print the turn action (if any)
                
            else:
                # If we haven't moved forward, try turning right before backtracking
                turn_action = 'turn_right'
                actions.append('turn_right')
                agent_dir = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}[agent_dir]
                print(f"({x}, {y}): {turn_action}")  # Print the turn action (if any)

            if path:  # <--- Add this check before the second pop()
                actions.append('move_forward')
                agent_pos = path.pop()
                print(f"({x}, {y}): move_forward to ({agent_pos[0]}, {agent_pos[1]})")

    target_pos = (0, 0)  # Set the target to the starting position
    visited = set()  # Reset visited set for returning

    while agent_pos != target_pos:
        x, y = agent_pos
        visited.add(agent_pos)

        # Explore safe adjacent cells
        safe_neighbors = []
        for dx, dy, direction in [(1, 0, 'south'), (-1, 0, 'north'), (0, 1, 'east'), (0, -1, 'west')]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in visited and is_safe_cell(nx, ny, solver):
                safe_neighbors.append((nx, ny, direction))

        if safe_neighbors:
            # Choose a safe neighbor (you can use different strategies here)
            nx, ny, direction = random.choice(safe_neighbors)  # Random choice for now

            # Determine actions to reach the chosen neighbor
            if agent_dir != direction:
                turn_action = 'turn_right' if (agent_dir, direction) in [('north', 'east'), ('east', 'south'), ('south', 'west'), ('west', 'north')] else 'turn_left'
                actions.append(turn_action)
                agent_dir = direction  # Update agent direction
            actions.append('move_forward')
            agent_pos = (nx, ny)
            path.append(agent_pos)
        else:
            if actions and actions[-1] == 'move_forward' and path:
                actions.append('turn_left')  # Turn around (could also use 'turn_right')
                actions.append('turn_left')
                actions.append('move_forward')
                agent_pos = path.pop()  # Remove the current position from the path
                # Recalculate agent direction (reverse of the previous direction)
                if agent_dir == 'north':
                    agent_dir = 'south'
                elif agent_dir == 'south':
                    agent_dir = 'north'
                elif agent_dir == 'east':
                    agent_dir = 'west'
                elif agent_dir == 'west':
                    agent_dir = 'east'
                print(f"({x}, {y}): {turn_action}")  # Print the turn action (if any)
                
            else:
                # If we haven't moved forward, try turning right before backtracking
                turn_action = 'turn_right'
                actions.append('turn_right')
                agent_dir = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}[agent_dir]
                print(f"({x}, {y}): {turn_action}")  # Print the turn action (if any)

            if path:  # <--- Add this check before the second pop()
                actions.append('move_forward')
                agent_pos = path.pop()
                print(f"({x}, {y}): move_forward to ({agent_pos[0]}, {agent_pos[1]})") 

    return path, actions

def write_output(path, actions, filename="output.txt"):
    """
    Writes the path and actions to the output file.

    Args:
        path (list): The list of positions in the path.
        actions (list): The list of actions taken by the agent.
        filename (str): The name of the output file.
    """
    with open(filename, 'w') as f:
        f.write(f"Path: {', '.join([str(p) for p in path])}\n")
        f.write(f"Actions: {', '.join(actions)}\n")

def find_gold_positions(map_data):
    """
    Finds the positions of all gold in the map data.

    Args:
        map_data (list): The 2D list representing the map.

    Returns:
        set: A set of tuples representing the gold positions.
    """
    gold_positions = set()
    for i in range(len(map_data)):
        for j in range(len(map_data[0])):
            if 'G' in map_data[i][j]:
                gold_positions.add((i, j))
    return gold_positions


def main():
    """Main function to run the Wumpus World agent."""

    grid_size, map_data, agent_pos = read_map("input.txt")

    # Initialize the solver and knowledge base
    solver = Glucose3()
    clauses = create_wumpus_clauses(grid_size)
    solver.append_formula(clauses)

    # Add initial percepts
    add_initial_percepts(agent_pos, map_data, solver)

    # Find the gold positions
    gold_positions = find_gold_positions(map_data)

    # Find the path to all golds and return to the starting position
    path, actions = find_path_to_all_golds(agent_pos, 'east', gold_positions, solver, grid_size, map_data)

    # Write the output
    write_output(path, actions)

if __name__ == "__main__":
    main()