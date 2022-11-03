import math

import numpy as np
from matplotlib import pyplot as plt
from numpy import nan

import EnvironmentDustin.Environment.EnvironmentTWIPR_objects as obj


def main():
    poles = [0, -20, -3 + 1j, -3 - 1j, 0, -1.5]
    eigenvectors = np.array([[1, nan, nan, nan, 0, nan],
                             [nan, 1, nan, nan, nan, nan],
                             [nan, nan, 1, 1, nan, 0],
                             [nan, nan, nan, nan, nan, nan],
                             [0, nan, nan, nan, 1, 1],
                             [nan, 0, 0, 0, nan, nan]])

    dyn_twipr = obj.TWIPR_Dynamics(model=obj.TWIPR_Michael_Model, Ts=0.02, poles=poles, ev=eigenvectors)

    dyn_twipr.state = np.asarray([2, 3, 0, 0, 0, math.pi / 2, 2])

    config = dyn_twipr.state.map(obj.Space3D_TWIPR())
    x = []
    for i in range(0, 250):
        dyn_twipr.update(input=[0.25, 0.25])
        x.append(dyn_twipr.state)

    theta = [state['x'].value for state in x]
    plt.figure()
    plt.plot(theta)
    plt.show()


if __name__ == '__main__':
    main()
