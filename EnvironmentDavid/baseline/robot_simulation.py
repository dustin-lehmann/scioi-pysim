import numpy as np


class RobotSimulation:
    position: list
    psi: float
    input: list
    Ts: float

    def __init__(self, Ts, position=None, psi=0):
        self.Ts = Ts
        if position is None:
            position = [0, 0]

        self.position = position
        self.psi = psi

    def update(self, input):
        self.position[0] = self.position[0] + self.Ts * input[0] * np.cos(self.psi)
        self.position[1] = self.position[1] + self.Ts * input[0] * np.sin(self.psi)
        self.psi = self.psi + self.Ts * input[1]

    def reset(self):
        self.position[0] = 0
        self.position[1] = 0
        self.psi = 0
