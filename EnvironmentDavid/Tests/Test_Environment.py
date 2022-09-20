import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.baseline.baseline_environment import BayblonVisualization
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
mapping_front_back = 0.65
mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    babylon_env: BayblonVisualization
    agent1: TankRobotSimObject
    agent2: TankRobotSimObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent1 = None
        self.agent2 = None
        self.babylon_env = None

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)

        if self.joystick.connected:
            # agent1 = self.world.getObjectsByName(name='Agent 1')[0]
            # agent1.dynamics.input = [self.joystick.axis[0], self.joystick.axis[1]]
            self.agent1.dynamics.input = [-self.joystick.axis[1] * mapping_front_back,
                                          -self.joystick.axis[2] * mapping_turn]

    # def world(self, *args, **kwargs):
    #     super().world(*args, **kwargs)
    #
    #     #create sample data

    def action_visualization(self, *args, **kwargs):
        super().action_visualization(*args, **kwargs)
        super().action_visualization(*args, **kwargs)

        sample = self.babylon_env.generateSample()
        self.babylon_env.webapp.sendSample(sample)
        time.sleep(0.001)

    def action_collision(self):
        """
        this function is going to do all the collision functions: - check if object is even collidable - **check
        spheres() (maybe Dustin already has a function that does exaclty that)** check if object/agents  sphere is
        close to an obstacle sphere - do collision checking → if true put collision points into min/max angle - from
        min/max angle create new function that handles the inputs for a robot
        """
        # loop through dict of alle the objects within testbed (real and simulated)
        for key in self.world.objects:
            # collision check is supposed to be done
            if self.world.objects[key].collision_check:
                for collision_object in self.world.objects:
                    # check if object even is collidable todo: dont do collision checking with oneself
                    if self.world.objects[collision_object].collidable is True:
                        # do sphere check
                        print('add sphere check!')

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        print("Init")

        # Init of Simulation Environment
        self.babylon_env = BayblonVisualization()
        self.babylon_env.wallsFromList(maze_coop2)
        # self.babylon_env.add_real_agent(self.agent1, self.agent2)
        self.babylon_env.add_simulated_agent(self.agent1)
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=0.1)
    # todo: sim objects haben keine abmaße? ->added
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)

    agent1 = TankRobotPhysicalObject()
    agent2 = TankRobotPhysicalObject()

    env.agent1 = agent1

    # env.agent2 = agent2

    # agent1.dynamics.input = [1, 0]

    def print_agent1_state(*args, **kwargs):
        pass
        # print(f"Agent 1 State: {agent1.dynamics.state}")

    core.scheduling.Action(name="Print Agent", function=print_agent1_state, parent=env.scheduling.actions['output'])
    core.scheduling.Action(name="Collision", function=env.action_collision, parent=env.scheduling.actions['input'])

    env.init(calltree=False)

    env.start()


if __name__ == '__main__':
    main()
