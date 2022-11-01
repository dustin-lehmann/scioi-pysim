import math

import EnvironmentDustin.Environment.EnvironmentTWIPR_objects as obj
import scioi_py_core.core as core


def main():
    twipr_space = obj.Space3D_TWIPR()
    space_3d = core.spaces.Space3D()

    state1 = twipr_space.getState()
    state1['pos'] = [1, 2]
    state1['theta'] = 1
    state1['psi'] = 1

    state2 = state1.map(space_3d)

    state3 = state2.map(twipr_space)
    pass


if __name__ == '__main__':
    main()
