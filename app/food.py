import app.movement as movement
import random
from Queue import PriorityQueue


def nearest_food_simple(data, weight):
    criteria = {"goal": "nearest_food_simple", "weight": weight}
    # picks closest food and gives direction towards it.
    food = data["board"]["food"]
    head = data["you"]["body"][0]
    width = data["width"]
    height = data["height"]

    nearest = nearest_food(head, food, width*height)

    directions = [0.1, 0.1, 0.1, 0.1]
    if nearest is not None:
        directions = movement.move_towards(head, nearest)

    criteria["direction_values"] = directions

    return criteria


def nearest_food(head, food, max):
    min_dist = max
    nearest = None

    for point in food:
        distance = movement.distance(head, point)
        if distance < min_dist:
            min_dist = distance
            nearest = point

    return nearest


def nearest_food_a_star(data, food_weight):
    criteria = {"goal": "find_nearest_food", "weight": food_weight} # TODO: we could vary weight depending on our snake's health

    # where we are
    us = data["you"]
    # first point in list is our head.
    our_head = us["body"][0]
    food = data["board"]["food"]
    width = data["board"]["width"]
    height = data["board"]["height"]

    goal = nearest_food(our_head, food, width*height)

    path = list()
    if goal is not None:
        path = a_star(our_head, goal, movement.get_grid(data))

    if len(path) == 0:
        directions = [1.0, 1.0, 1.0, 1.0]
    else:
        first = path[0]
        first_point = {"x": first[0], "y": first[1]}

        directions = movement.move_towards(our_head, first_point)

    directions = [(x * random.random()) * 2 for x in directions]

    # normalize weighting matrix
    if sum(directions) == 0:
        criteria["direction_values"] = [0.0, 0.0, 0.0, 0.0]
    else:
        criteria["direction_values"] = [x / sum(directions) for x in directions]

    return criteria


def to_tuple(point):
    return (point["x"], point["y"])


def a_star(start, goal, grid):
    closedList = [] # Squares we don't need to consider anymore
    openList = PriorityQueue() # Squares we do need to consider
    openList.put((0, start))
    came_from = {}
    cost_so_far = {}

    came_from[to_tuple(start)] = None
    cost_so_far[to_tuple(start)] = 0

    while not openList.empty():
        current = openList.get() # Remove square with lowest f score
        current_point = current[1]
        closedList.append(current) # add current square to closed list

        if goal["x"] == current_point["x"] and goal["y"] == current_point["y"]:
            break

        for i in range(4):
            new_point = movement.move_point(current_point, i)

            shape = grid.shape
            if new_point["x"] < 0 or new_point["x"] >= shape[0]:
                continue

            if new_point["y"] < 0 or new_point["y"] >= shape[1]:
                continue

            if grid[new_point["x"]][new_point["y"]] == movement.SNAKE:
                continue

            new_cost = cost_so_far[to_tuple(current_point)] + 1

            if to_tuple(new_point) not in cost_so_far or new_cost < cost_so_far[to_tuple(new_point)]:
                cost_so_far[to_tuple(new_point)] = new_cost
                priority = new_cost + manhattan_distance(new_point, goal)
                openList.put((priority, new_point))
                came_from[to_tuple(new_point)] = to_tuple(current_point)

    return build_path(start, goal, came_from)


def build_path(start, goal, came_from):
    current_point = to_tuple(goal)
    path = list()

    #print(came_from)

    while current_point != to_tuple(start):
        if current_point in came_from:
            path.append(current_point)
            current_point = came_from[current_point]
        else:
            break

    path.reverse()

    return path

# to calculate g, add 1 to G of its parent
    # G is movement cost from start point to current square
    # H is estimated movement cost from the current square to the destination (heuristic)


# F is score of each square. F = G + H
def manhattan_distance(p1, p2):

    return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])