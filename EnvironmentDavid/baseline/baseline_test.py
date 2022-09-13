from scioi_ritl.application.lndw.core.objects import ObstacleBox, TileBoxOrientation, Environment, BoxPlot
from scioi_ritl.application.lndw.baseline.baseline_environment import BaselineEnvironment

maze_left_vs = [
    ['h', 0, 1, 1],
    ['h', 1, 2, 1],
    ['h', 0, 3, 1],
    ['h', 1, 4, 1],
    ['v', 2, 1, 4],
    ['v', 3, 1, 3],
    ['v', 4, 2, 1],
    ['v', 5, 2, 1],
    ['h', 4, 3, 1],
    ['h', 7, 2, 2],
    ['h', 3, 4, 3],
    ['h', 2, 5, 4],
    ['v', 6, 4, 1],
    ['h', 6, 3, 2],
    ['h', 7, 4, 1],
    ['v', 7, 4, 1],
    ['h', 7, 5, 2],
    ['v', 1, 5, 1],
    ['h', 1, 5, 5],
    ['h', 7, 6, 1],
    ['h', 0, 7, 1],
    ['h', 5, 7, 1],
    ['h', 8, 7, 1],
    ['v', 2, 7, 1],
    ['v', 6, 6, 2],
    ['v', 8, 7, 1],
    ['h', 0, 8, 2],
    ['v', 3, 7, 3],
    ['v', 1, 9, 1],
    ['h', 1, 10, 1],
    ['v', 2, 9, 1],
    ['h', 3, 10, 3],
    ['v', 6, 9, 1],
    ['h', 4, 9, 2],
    ['v', 4, 8, 1],
    ['h', 4, 8, 1],
    ['v', 5, 7, 1],
    ['h', 6, 8, 1],
    ['v', 8, 9, 2],
    ['h', 8, 11, 1],
    ['v', 7, 10, 2],
    ['h', 0, 12, 1],
    ['v', 1, 11, 1],
    ['v', 2, 11, 1],
    ['h', 2, 11, 4],
    ['v', 6, 11, 2],
    ['v', 7, 10, 2],
    ['h', 7, 12, 1]
]


def main():
    env = BaselineEnvironment()
    env.wallsFromList(maze_left_vs)
    j = env.toJson(file="../babylon/objects.json")

    BoxPlot(env.walls, collision=False)

    pass


if __name__ == '__main__':
    main()
