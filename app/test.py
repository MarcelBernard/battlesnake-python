import app.main as main
import time
import app.movement as movement


def run_tests(data):

    start = time.time()

    print("make sure move throws no errors")
    print(main.execute_move(data))

    grid = movement.get_grid(data)

    end = time.time()

    print(str.format("took {0:.1f} ms", (end - start)*1000))


if __name__ == "__main__":

    test_data = {
      "game": {
        "id": "game-id-string"
      },
      "turn": 1,
      "board": {
        "height": 11,
        "width": 11,
        "food": [{
          "x": 1,
          "y": 3
        }],
        "snakes": [{
          "id": "snake-id-string",
          "name": "Sneky Snek",
          "health": 100,
          "body": [{
            "x": 1,
            "y": 3
          }]
        }]
      },
      "you": {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 100,
        "body": [{
          "x": 1,
          "y": 3
        }]
      }
    }

    run_tests(test_data)
