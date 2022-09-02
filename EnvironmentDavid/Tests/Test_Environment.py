import qmt

import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject


class EnvironmentDavid_thisExample(EnvironmentDavid):
    agent1: TankRobotSimObject
    agent2: TankRobotSimObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = None
        self.agent2 = None

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)

        if self.joystick.connected:
            # agent1 = self.world.getObjectsByName(name='Agent 1')[0]
            # agent1.dynamics.input = [self.joystick.axis[0], self.joystick.axis[1]]
            self.agent1.dynamics.input = [self.joystick.axis[0], self.joystick.axis[1]]
        else:
            pass

    def action_visualization(self, *args, **kwargs):
        super().action_visualization(*args, **kwargs)
        print("here comes the babylon stuff")

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        print("Here comes the whole init stuff")


def main():
    env = EnvironmentDavid_thisExample(Ts=1)
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    agent2 = TankRobotSimObject(name='Agent 2', world=env.world)

    env.agent1 = agent1
    env.agent2 = agent2

    agent1.dynamics.input = [1, 0]

    def print_agent1_state(*args, **kwargs):
        print(f"Agent 1 State: {agent1.dynamics.state}")

    core.scheduling.Action(name="Print Agent", function=print_agent1_state, parent=env.scheduling.actions['output'])

    env.init(calltree=False)

    env.start()


if __name__ == '__main__':
    main()
