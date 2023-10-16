import json

from applications.TWIPR_Simple.Environment.Environments.environment_base import EnvironmentBase
from applications.TWIPR_Simple.Environment.EnvironmentTWIPR_objects import TWIPR_Agent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
from scioi_py_core.utils.babylon import setBabylonSettings

wait_steps = 100


class Environment_TransferLearning(EnvironmentBase):
    agent1: TWIPR_Agent
    agent2: TWIPR_Agent
    obstacle1: CuboidObstacle_3D

    data: dict

    phase: str
    k: int

    def __init__(self, experiment, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('two_twiprs_ilc.json') as data_file:
            data = json.load(data_file)

        webapp_title = ''
        if experiment == 'transfer':
            webapp_title = 'Dynamic Transfer'
            self.experiment_len = len(data['ilc']['agent_1'][0])
            self.agent_1_data = {
                'x': [0] * wait_steps + data['ilc']['agent_1'][0] + [data['ilc']['agent_1'][0][-1]] * wait_steps,
                'y': [-0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['ilc']['agent_1'][2] + [data['ilc']['agent_1'][2][-1]] * wait_steps
            }
            self.agent_2_data = {
                'x': [0] * wait_steps + data['ilc']['agent_2_transfer'][0] + [
                    data['ilc']['agent_2_transfer'][0][-1]] * wait_steps,
                'y': [0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['ilc']['agent_2_transfer'][2] + [
                    data['ilc']['agent_2_transfer'][2][-1]] * wait_steps,
            }
        elif experiment == 'direct':
            webapp_title = 'Direct Transfer'
            self.experiment_len = len(data['ilc']['agent_1'][0])
            self.agent_1_data = {
                'x': [0] * wait_steps + data['ilc']['agent_1'][0] + [data['ilc']['agent_1'][0][-1]] * wait_steps,
                'y': [-0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['ilc']['agent_1'][2] + [data['ilc']['agent_1'][2][-1]] * wait_steps
            }
            self.agent_2_data = {
                'x': [0] * wait_steps + data['ilc']['agent_2_direct'][0] + [
                    data['ilc']['agent_2_direct'][0][-1]] * wait_steps,
                'y': [0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['ilc']['agent_2_direct'][2] + [
                    data['ilc']['agent_2_direct'][2][-1]] * wait_steps,
            }
        elif experiment == 'estimation':
            webapp_title = 'Estimation'
            self.experiment_len = len(data['estimation']['agent_1'][0])
            self.agent_1_data = {
                'x': [0] * wait_steps + data['estimation']['agent_1'][0] + [
                    data['estimation']['agent_1'][0][-1]] * wait_steps,
                'y': [-0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['estimation']['agent_1'][2] + [
                    data['estimation']['agent_1'][2][-1]] * wait_steps
            }
            self.agent_2_data = {
                'x': [0] * wait_steps + data['estimation']['agent_2'][0] + [
                    data['estimation']['agent_2'][0][-1]] * wait_steps,
                'y': [0.4] * (self.experiment_len + 2 * wait_steps),
                'psi': [0] * (self.experiment_len + 2 * wait_steps),
                'theta': [0] * wait_steps + data['estimation']['agent_2'][2] + [
                    data['estimation']['agent_2'][2][-1]] * wait_steps
            }
        setBabylonSettings(title=webapp_title)

        self.agent1 = TWIPR_Agent(world=self.world, agent_id=1, speed_control=True)
        self.agent2 = TWIPR_Agent(world=self.world, agent_id=2, speed_control=True)

        self.agent1.setPosition(y=-0.4, x=-1.2)
        self.agent2.setPosition(y=0.4, x=-1.2)

        fl1 = floor.generateTileFloor(self.world, tiles=[10, 1], tile_size=0.4)

        fl2 = floor.generateTileFloor(self.world, tiles=[10, 1], tile_size=0.4)

        fl1.setPosition(y=-0.4)
        fl2.setPosition(y=0.4)

        self.phase = 'agent_1'
        self.k = 0

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

        if self.phase == 'agent_1':
            self.agent1.setConfiguration([[self.agent_1_data['x'][self.k] - 1.2, self.agent_1_data['y'][self.k]],
                                          self.agent_1_data['theta'][self.k],
                                          self.agent_1_data['psi'][self.k]])

        elif self.phase == 'agent_2':
            self.agent2.setConfiguration([[self.agent_2_data['x'][self.k] - 1.2, self.agent_2_data['y'][self.k]],
                                          self.agent_2_data['theta'][self.k],
                                          self.agent_2_data['psi'][self.k]])

        self.k = self.k + 1

        if self.k == self.experiment_len + wait_steps:
            if self.phase == 'agent_1':
                self.k = 0
                self.phase = 'agent_2'
            elif self.phase == 'agent_2':
                self.phase = 'done'

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        # self.agent2.input = [-2 * self.joystick.axis[1], -4 * self.joystick.axis[2]]


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
