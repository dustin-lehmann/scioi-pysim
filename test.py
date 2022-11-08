import math

import numpy as np


class NewFloat:
    x: float

    def __init__(self, x):
        self.x = x

    def __float__(self):
        return float(self.x)


class NewArray(np.ndarray):
    names: list

    def __init__(self, values):
        shape = (len(values),)
        super().__init__(shape)





def main():
    x = np.asarray([1,2,3])

    pass


if __name__ == '__main__':
    main()
