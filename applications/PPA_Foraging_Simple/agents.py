import math

import numpy as np

SAMPLE_TIME = 0.01
class Agent:
    state: list
    input: list
    goal_position: list
    v_max = 1
    psi_dot_max = math.pi/2

    def __init__(self):
        self.state = [0, 0, 0] # x, y, psi
        self.input = [0, 0] # v, psi_dot
        self.goal_position = [0, 0] # x, y

    def setGoalPosition(self, goal_position):
        self.goal_position = goal_position

    def control(self):
        pass

    def setInput(self, input):
        self.input = input

    def setPosition(self, position):
        self.state[0] = position[0]
        self.state[1] = position[1]

    def setOrientation(self, orientation):
        self.state[2] = orientation

    def setState(self, state):
        self.state = state

    def update(self):
        self.control()
        v = self.input[0]
        psi_dot = self.input[1]

        if v > self.v_max:
            v = self.v_max
        if v < -self.v_max:
            v = -self.v_max
        if psi_dot > self.psi_dot_max:
            psi_dot = self.psi_dot_max
        if psi_dot < -self.psi_dot_max:
            psi_dot = -self.psi_dot_max

        self.state[0] += SAMPLE_TIME * v * np.cos(self.state[2])
        self.state[1] += SAMPLE_TIME * v * np.sin(self.state[2])
        self.state[2] += SAMPLE_TIME * psi_dot

        if self.state[2] > math.pi:
            self.state[2] -= 2*math.pi
        if self.state[2] < -math.pi:
            self.state[2] += 2*math.pi

