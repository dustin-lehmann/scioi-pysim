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


def rotmatFromPsi_2D(psi):
    out = np.asarray([[np.cos(psi), -np.sin(psi)], [np.sin(psi), np.cos(psi)]])
    return out


def psiFromRotMat(rotmat):
    q = qmt.quatFromRotMat(rotmat)
    angles = qmt.eulerAngles(q, 'zxy', intrinsic=True)
    assert (angles[1] < 1e-4 and angles[2] < 1e-4)
    return angles[0]


def twiprToRotMat(theta, psi):
    q = qmt.quatFromEulerAngles(np.asarray([psi, theta, 0]), 'zyx')
    out = qmt.quatToRotMat(q)
    return out


def twiprFromRotMat(rotmat):
    q = qmt.quatFromRotMat(rotmat)
    angles = qmt.eulerAngles(q, 'zyx')
    out = angles[0], angles[1]
    return out
