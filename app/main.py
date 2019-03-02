import bottle
import os
import random

import app.collisions as collisions
import app.freedom as freedom
import app.food as food


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#FF0000',
        'taunt': 'noodly noodly',
        'head_url': head_url,
        'name': 'danger-noodle',
        'head_type': 'tongue',
        'tail_type': 'freckled',
        'secondary_color': '#FFFF00'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    return execute_move(data)


@bottle.post('/end')
def end():
    # return something
    return {}


@bottle.post('/ping')
def ping():
    # return something
    return {}

    
def execute_move(data):
    
    directions = ['up', 'down', 'left', 'right']
    direction_weights = get_direction_weights(data)
    weights_string = str.format("up: {0:.2f}, down: {1:.2f}, left: {2:.2f}, right: {3:.2f}",
                                direction_weights[0], direction_weights[1], direction_weights[2], direction_weights[3])
    print(weights_string)

    # get index of maximum value in direction_weights
    max_weight, index = choose_direction(direction_weights)

    if max_weight == 0:
        return {
            'move': directions[index],
        }

    return {
        'move': directions[index],
    }


def choose_direction(weights):
    best_weight = max(weights)
    good_directions = [i for i, x in enumerate(weights) if x == best_weight]

    # If multiple equivalent directions exist, pick one at random.
    return best_weight, random.choice(good_directions)


def get_direction_weights(data):
    # pick a direction to move
    weights = list()

    # The direction weights and decision weights added at the same time,
    weights.append(collisions.avoid_walls(data, 1))
    weights.append(collisions.avoid_other_snakes(data, 10))
    weights.append(collisions.chaos_reigns(data, 5))
    # weights.append(freedom.move_to_most_space(data, 4))


    longest_snake = 0
    our_snake = len(data["you"]["body"])

    for snake in data["board"]["snakes"]:
        if len(snake["body"]) > longest_snake:
            longest_snake = len(snake["body"])

    health = data["you"]["health"]
    if health == 0:
        # we are dead
        return [1.0, 1.0, 1.0, 1.0]

    if our_snake <= longest_snake:
        weights.append(food.nearest_food_a_star(data, (1.0 / health) * 10))
    elif health > 70:
        weights.append(collisions.follow_tail(data, 3))
    else:
        weights.append(food.nearest_food_a_star(data, (1.0 / health) * 10))

    print(weights)

    return combine_weights_add(weights)


def combine_weights_multiply(weights):
    # combine weights produced by each factor according to their weight
    combined_weights = [1.0, 1.0, 1.0, 1.0]

    for criteria in weights:
        criteria_weight = criteria["weight"]
        direction_values = criteria["direction_values"]
        direction_values = [x*criteria_weight for x in direction_values]
        combined_weights = [x*y for x, y in zip(combined_weights, direction_values)]

    if sum(combined_weights) == 0:
        return [0.0, 0.0, 0.0, 0.0]

    return [x/sum(combined_weights) for x in combined_weights]


def combine_weights_add(weights):
    # combine weights produced by each factor according to their weight
    combined_weights = [1.0, 1.0, 1.0, 1.0]

    for criteria in weights:
        criteria_weight = criteria["weight"]
        direction_values = criteria["direction_values"]

        for i in range(4):
            new_val = direction_values[i]*criteria_weight
            if new_val == 0:
                combined_weights[i] = 0
            elif combined_weights[i] != 0:
                combined_weights[i] += new_val

    if sum(combined_weights) == 0:
        return [0.0, 0.0, 0.0, 0.0]

    return [x/sum(combined_weights) for x in combined_weights]


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
