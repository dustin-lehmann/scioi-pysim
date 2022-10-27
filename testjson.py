import numpy as np

import scioi_py_core.core as core
import json


def main():
    space = core.spaces.Space3D()
    state = space.getState()

    p = state.serialize()

    x = {
        'x': state
    }

    d = json.dumps(x, default=core.spaces.dumper)
    pass


if __name__ == '__main__':
    main()
