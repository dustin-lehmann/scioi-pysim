import dataclasses
from abc import ABC
from EnvironmentDavid.baseline.baseline_environment import BabylonVisualization

class tester:
    @property
    def return_dict(self):
        x = 3
        y = 2
        diggi = {
            'x' : x,
            'y' : y
        }
        return diggi




if __name__ == '__main__':
    ted = tester()
    y=ted.return_dict['y']
    power = ted.return_dict['x']**2
    print(y)


    print('ende')
