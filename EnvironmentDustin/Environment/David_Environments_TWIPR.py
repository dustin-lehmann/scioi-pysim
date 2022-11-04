import math


from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentBase
from EnvironmentDustin.Environment.EnvironmentTWIPR_objects import TankRobotSimObject, TWIPR_Agent, TWIPR_DynamicAgent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core


class Environment_SingleTWIPR_ILC(EnvironmentBase):
    agent1: TWIPR_DynamicAgent
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_DynamicAgent(agent_id=1, name='Agent 1', world=self.world, speed_control=True)

        floor.generateTileFloor(self.world, tiles=[8, 3], tile_size=0.4)

        self.agent1.state['x'] = -1
        self.agent1.state['psi'] = -math.pi

        group1 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())

        group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=0.15,
                                                         position=[0, 0.2, 0.075])
        group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=0.15,
                                                         position=[0, -0.2, 0.075])
        group_object3 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.44, size_z=0.04,
                                                         position=[0, 0, 0.17])

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        self.agent1.input = [-2 * self.joystick.axis[1], -4 * self.joystick.axis[2]]
        pass


def main():
    env = Environment_SingleTWIPR_ILC(visualization='babylon', webapp_config={'title': 'Single Agent ILC'})
    env.init()
    env.start()


if __name__ == '__main__':
    main()
