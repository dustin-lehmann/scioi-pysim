import dataclasses
from abc import ABC
from EnvironmentDavid.baseline.baseline_environment import BabylonVisualization


class A:
    def __init__(self):
        self.a = 1

class B(A):
    def __init__(self):
        self.a = 2
        super().__init__()




if __name__ == '__main__':
    ted = B()



    print('ende')
