import pickle

from applications.TWIPR_Simple.Environment.Environments.environment_base import EnvironmentBase
from applications.TWIPR_Simple.Environment.EnvironmentTWIPR_objects import TWIPR_ILC_Agent, \
    standard_reference_trajectory, TWIPR_Agent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.core.scheduling import Action
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core
from scioi_py_core.utils.babylon import setBabylonSettings


class Environment_CILC(EnvironmentBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_Agent(world=self.world, agent_id=1)
        self.agent2 = TWIPR_Agent(world=self.world, agent_id=2)
        self.agent3 = TWIPR_Agent(world=self.world, agent_id=3)

        self.agents = [self.agent1, self.agent2, self.agent3]

        self.agent_x_offset = -0.35
        self.y_offset = 0.8
        post_height = 0.12
        # Agent 2
        fl1 = floor.generateTileFloor(self.world, tiles=[10, 1], tile_size=0.4)
        self.agent2.setPosition(x=self.agent_x_offset)
        group1 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())
        group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, 0.2, post_height / 2])
        group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, -0.2, post_height / 2])
        group_object3 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.44, size_z=0.04,
                                                         position=[0, 0, post_height + 0.04 / 2])

        # Agent 1
        fl2 = floor.generateTileFloor(self.world, tiles=[10, 1], tile_size=0.4)
        fl2.setPosition(y=-self.y_offset)
        self.agent1.setPosition(y=-self.y_offset, x=self.agent_x_offset)
        group2 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())
        group_object1 = core.obstacles.CuboidObstacle_3D(group=group2, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, 0.2, post_height / 2])
        group_object2 = core.obstacles.CuboidObstacle_3D(group=group2, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, -0.2, post_height / 2])
        group_object3 = core.obstacles.CuboidObstacle_3D(group=group2, size_x=0.04, size_y=0.44, size_z=0.04,
                                                         position=[0, 0, post_height + 0.04 / 2])
        group2.setPosition(y=-self.y_offset)

        # Agent 3
        fl3 = floor.generateTileFloor(self.world, tiles=[10, 1], tile_size=0.4)
        fl3.setPosition(y=self.y_offset)
        self.agent3.setPosition(y=self.y_offset, x=self.agent_x_offset)
        group3 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())
        group_object1 = core.obstacles.CuboidObstacle_3D(group=group3, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, 0.2, post_height / 2])
        group_object2 = core.obstacles.CuboidObstacle_3D(group=group3, size_x=0.04, size_y=0.04, size_z=post_height,
                                                         position=[0, -0.2, post_height / 2])
        group_object3 = core.obstacles.CuboidObstacle_3D(group=group3, size_x=0.04, size_y=0.44, size_z=0.04,
                                                         position=[0, 0, post_height + 0.04 / 2])

        group3.setPosition(y=self.y_offset)

        with open('ecilc_data.p', 'rb') as file:
            self.ecilc_data = pickle.load(file)

        for idx, agent in enumerate(self.agents):
            agent.data = self.ecilc_data[str(idx + 1)]['trials']
            agent.collision_during_trial = False

        self.j = 0
        self.K = len(self.agent1.data[0]['x'])
        self.J = len(self.agent1.data)
        self.k = 0
        self.collision = False
        self.finished_flag = False
        self.wait_steps = 20
        self.trial_state = 'wait_before_trial'

        Action(function=self.input, parent=self.world.scheduling.actions['input'])
        Action(function=self.entry, parent=self.world.scheduling.actions['_entry'])
        Action(function=self.update_after_step, parent=self.world.scheduling.actions['logic2'])

    # ====

    def update_after_step(self):
        if self.k == self.K - 1:
            self.update_after_trial()
        else:
            if self.trial_state == 'trial':
                for agent in self.agents:
                    agent.collision_during_trial = agent.collision_during_trial or agent.physics.collision.collision_state
            self.k = self.k + 1

    def update_after_trial(self):

        if self.finished_flag:
            return

        if any((not(agent.collision_during_trial) and agent.configuration['pos']['x'] > 0.0) for agent in self.agents) and self.j > 5:

            # Agents managed to do it
            # setBabylonSettings(background_color=[29 / 255, 145 / 255, 31 / 255])
            self.finished_flag = True
        else:
            ...
            # setBabylonSettings(background_color=[29 / 255, 145 / 255, 31 / 255])
            # setBabylonSettings(background_color=[242 / 255, 56 / 255, 56 / 255])

        if self.j == 2:
            pass
        # self.collision = self.collision or any(agent.physics.collision.collision_state for agent in self.agents)
        # if self.collision:
        #     setBabylonSettings(background_color=[242 / 255, 56 / 255, 56 / 255])

        if self.j == self.J - 1:
            self.finished_flag = True

        self.trial_state = 'wait_after_trial'
        self.collision = False
        self.k = 0
        self.j = self.j + 1

    def input(self):
        if not self.finished_flag:
            if self.trial_state == 'trial':
                for agent in self.agents:
                    x = agent.data[self.j]['x'][self.k][0] + self.agent_x_offset
                    theta = agent.data[self.j]['x'][self.k][2]
                    agent.setPosition(x=x)
                    agent.setConfiguration(dimension='theta', value=theta)
                    pass
            elif self.trial_state == 'wait_after_trial' or self.trial_state == 'wait_before_trial':
                pass
                # self.input = [0, 0]
        else:
            pass

    def entry(self):
        if self.j == 0:
            setBabylonSettings(status=f"Trial 0")
        if not self.finished_flag:
            if self.trial_state == 'wait_before_trial' and self.k == self.wait_steps:
                self.k = 0
                self.trial_state = 'trial'
            elif self.trial_state == 'wait_after_trial' and self.k == self.wait_steps:
                self.k = 0
                self.trial_state = 'wait_before_trial'
                setBabylonSettings(status=f"Trial {self.j}")
                setBabylonSettings(background_color=0)
                for agent in self.agents:
                    agent.setConfiguration(dimension='theta', value=0)
                    agent.setPosition(x=self.agent_x_offset)
                    agent.collision_during_trial = False


def main():
    env = Environment_CILC(visualization='babylon',
                           webapp_config={'title': 'Cooperative ILC', 'record': {'file': 'cilc.webm', 'time': 40}})
    env.init()
    env.start()


if __name__ == '__main__':
    main()
