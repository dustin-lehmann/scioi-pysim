import json

from applications.TWIPR_Simple.Environment.Environments.environment_base import EnvironmentBase
from applications.TWIPR_Simple.Environment.EnvironmentTWIPR_objects import TWIPR_Agent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
from scioi_py_core.utils.babylon import setBabylonSettings

wait_steps = 100


class Environment_TransferLearning(EnvironmentBase):
    agent1: TWIPR_Agent
    obstacle1: CuboidObstacle_3D

    def __init__(self, experiment, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent1 = TWIPR_Agent(world=self.world, agent_id='generic', speed_control=True)

        self.agent1.setPosition(y=0, x=0)
        fl1 = floor.generateTileFloor(self.world, tiles=[1, 1], tile_size=0.3)

        # fl1.setPosition(y=-0.4)





def main():
    env = Environment_TransferLearning(experiment='direct', visualization='babylon',
                                       webapp_config={'title': 'Direct Transfer',
                                                      'record': {'file': 'estimation.webm', 'time': 20},
                                                      'background': [1, 1, 1]})
    setBabylonSettings(background_color=[1, 1, 1])
    env.init()
    env.start()
    ...


if __name__ == '__main__':
    main()
