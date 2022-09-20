import numpy as np

from scioi_ritl.application.lndw.core.objects import Box, BoxPlot


def main():

    box1 = Box(center=[0,0], size_x=2000, size_y=1000, psi=0)
    box2 = Box(center=[1080, 600], size_x=500, size_y=1000, psi=np.deg2rad(45))
    collided_areas, _ = box2.collisionCheck(box1)
    print(collided_areas)
    BoxPlot([box1, box2])


if __name__ == '__main__':
    main()