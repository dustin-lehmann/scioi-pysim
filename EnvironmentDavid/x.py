import numpy as np
import qmt


def main():
    x1 = np.asarray([1, 0, 0])
    x2 = np.asarray([0, 2, 0])

    angle = qmt.angleBetween2Vecs(x1, x2)
    print(angle)


if __name__ == '__main__':
    main()
