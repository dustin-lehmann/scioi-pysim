from applications.TWIPR_Simple.Environment.Environments.environment_base import EnvironmentBase
from applications.TWIPR_Simple.Environment.EnvironmentTWIPR_objects import TWIPR_ILC_Agent, \
    standard_reference_trajectory
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core


class Environment_SingleTWIPR_ILC(EnvironmentBase):
    agent1: TWIPR_ILC_Agent
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_ILC_Agent(world=self.world, agent_id=1, r=0.07, s=1,
                                      reference=standard_reference_trajectory)

        floor.generateTileFloor(self.world, tiles=[6, 1], tile_size=0.4)

        group1 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())

        post_height = 0.13
        group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, 0.2, post_height / 2])
        group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, -0.2, post_height / 2])
        group_object3 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.44, size_z=0.04,
                                                         position=[0, 0, post_height + 0.04 / 2])

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)


def main():
    env = Environment_SingleTWIPR_ILC(visualization='babylon', webapp_config={'title': 'Single Agent ILC', 'record': {
        'file': 'single_agent_ilc.webm', 'time': 92}})
    env.init()
    env.start()


if __name__ == '__main__':
    main()
