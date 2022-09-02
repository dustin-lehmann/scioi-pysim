import numpy as np
import qmt as qmt


def rotmatFromEuler(angles, convention):
    if isinstance(angles, list):
        angles = np.asarray(angles)
    q = qmt.quatFromEulerAngles(angles, convention)
    return qmt.quatToRotMat(q)


def rotmatFromPsi(psi):
    q = qmt.quatFromAngleAxis(angle=psi, axis=[0, 0, 1])
    return qmt.quatToRotMat(q)
