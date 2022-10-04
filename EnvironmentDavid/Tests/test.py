import dataclasses
from abc import ABC
from EnvironmentDavid.baseline.baseline_environment import BabylonVisualization


class Test:
    def __init__(self):
        self.a = 1


class Tester(Test):
    def __init__(self):
        super().__init__()


class Buch:
    dictionary: dict[str, 'test']
    def __init__(self,tester):
        self.dictionary: dict[str, 'test'] = {}
        self.dictionary[0] = tester

if __name__ == '__main__':
    tester = Tester()
    buch = Buch(tester)
    item = buch['0']


    print('ende')
