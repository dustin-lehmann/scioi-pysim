from applications.TWIPR_Simple.Environment.Environments.Environment_SingleTWIPR import Environment_SingleTWIPR, Environment_SingleTWIPR_KeyboardInput
from scioi_py_core.objects.world import floor
from scioi_py_core.objects.world.grid import Grid2D
import scioi_py_core.core as core


def main():
    env = Environment_SingleTWIPR_KeyboardInput(visualization='babylon', webapp_config={'title': 'This is a title'})
    floor = Grid2D(env.world, cell_size=0.5, cells_x=10, cells_y=10, origin=[0, 0])

    group1 = core.world.WorldObjectGroup(name='Gate', world=env.world, local_space=core.spaces.Space3D())
    # group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.1, size_y=0.1, size_z=0.2,
    #                                                  position=[0, 0.5, 0.1])
    # group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.1, size_y=0.1, size_z=0.2,
    #                                                  position=[0, -0.5, 0.1])

    env.init()
    env.start()




# TODO: Implement the translate and rotate functions. Also make some objects fixed so that changing
#  any in their config gives an error

if __name__ == '__main__':
    main()
