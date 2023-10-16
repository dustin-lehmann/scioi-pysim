import math
import time
from threading import Thread

import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.patches import Wedge, Circle, FancyArrowPatch, Rectangle
matplotlib.use('qtagg')


class PlotObject_S2DV:
    id: str

    def __init__(self, id):
        self.id = id

class Agent_S2DV(PlotObject_S2DV):
    ax: plt.Axes
    marker: Circle
    arrow: FancyArrowPatch
    position: list
    psi: float

    circle_radius = 0.075
    arrow_head = 0.08
    arrow_length = 0.3
    color = 'red'

    def __init__(self, ax, id, color = None):
        super().__init__(id)
        self.id = id
        self.ax = ax
        self.position = [0, 0]

        if color is not None:
            self.color = color

        self.draw()
        self.update(0, 0, 0)

    def draw(self):
        self.marker = Circle((self.position[0], self.position[1]), radius=self.circle_radius, alpha=0.5,
                                   color=self.color)
        self.ax.add_artist(self.marker)
        self.arrow = FancyArrowPatch(posA=(0, 0),
                                     posB=(0, 0),
                                     arrowstyle='simple', mutation_scale=10, color=self.color, alpha=0.75)

        self.ax.add_artist(self.arrow)

    def update(self, x, y, psi):
        self.position = [x, y]
        self.psi = psi

        # text = "({:d}) [{:.1f},{:.1f},{:.1f}]".format(self.id, x, y, math.degrees(psi))
        # if 0 < psi < math.pi:
        #     self.text.set_position((x, y - 0.3))
        # else:
        #     self.text.set_position((x, y + 0.2))
        # self.text.set_text(text)

        self.marker.center = (x, y)
        # self.cone.update({'center': (x, y), 'theta1': math.degrees(self.psi) - self.vision_fov / 2,
        #                   'theta2': math.degrees(self.psi) + self.vision_fov / 2})

        self.arrow.set_positions((x + 0.8 * self.circle_radius * math.cos(self.psi),
                                  y + 0.8 * self.circle_radius * math.sin(self.psi)),
                                 (x + self.arrow_length * math.cos(self.psi),
                                  y + self.arrow_length * math.sin(self.psi))
                                 )

class GridTile_S2DV(PlotObject_S2DV):
    rect: Rectangle
    position: list
    size: float
    ax: plt.Axes

    def __init__(self, ax, id, position, size):
        super().__init__(id)
        self.id = id
        self.ax = ax
        self.position = position
        self.size = size
        self.rect = Rectangle((self.position[0]-self.size/2, self.position[1]-self.size/2), self.size, self.size, edgecolor=(0,0,0,0.1), facecolor=(1,1,1,0.2))
        self.ax.add_artist(self.rect)

    def highlight(self, state, color=None):
        if color is None:
            color = (1,0,0,0.2)
        if isinstance(color, str):
            color = matplotlib.colors.to_rgba(color, alpha=0.2)
        elif isinstance(color, list):
            color = matplotlib.colors.to_rgba(color, alpha=0.2)
        if not state:
            color = (1,1,1,0.2)

        self.rect.set_facecolor(color)

class Grid_S2DV:
    tiles = list[GridTile_S2DV]
    size_x : list
    size_y: list

    def __init__(self, ax, size_x, size_y, tile_size):
        self.size_x = size_x
        self.size_y = size_y
        self.tile_size = tile_size
        self.ax = ax
        self.tiles = []

    def draw(self):
        num_tiles_x = int((self.size_x[1] - self.size_x[0]) / self.tile_size)
        num_tiles_y = int((self.size_y[1] - self.size_y[0]) / self.tile_size)
        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                self.tiles.append(GridTile_S2DV(self.ax, "hello", [self.size_x[0] + self.tile_size/2 +  i * self.tile_size, self.size_y[0] + self.tile_size/2 + j * self.tile_size], self.tile_size))



class World_S2DV:
    ...




class Simple2DVisualization:
    size: list
    ax: plt.Axes
    agents: list[Agent_S2DV]
    fetch_function: callable
    config: dict

    thread: Thread

    def __init__(self, fetch_function: callable = None, *args, **kwargs):
        self.size_y = None
        self.size_x = None
        self.fig = None
        self.ax = None
        self.agents = []
        self.fetch_function = fetch_function
        self.config = None
        self.thread = None

    def setWorldConfig(self, config: dict):
        self.init([-1,1], [-1,1])
        print("HELLO")


    def init(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        # Create an empty matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.ax.set(xlabel='x', ylabel='y', xlim=(self.size_x[0], self.size_x[1]), ylim=(self.size_y[0], self.size_y[1]))
        self.ax.set_aspect('equal', 'box')

        Grid_S2DV(self.ax, self.size_x, self.size_y, 0.5)


    def add_agent(self):
        agent = Agent_S2DV(self.ax, 'hello')
        self.agents.append(agent)
        return agent

    def start(self):
        # plt.ion()
        plt.draw()
        self.test_plot()
        plt.pause(1)
        # self.thread = Thread(target=self.thread_function)
        # self.thread.start()

    def test_plot(self):
        # Generate a random 2D point
        point = np.random.rand(2)
        self.fig.axes[0].plot(point)
        plt.draw()
        plt.pause(1)

    def thread_function(self):
        while True:
            plt.pause(1)
            time.sleep(1)