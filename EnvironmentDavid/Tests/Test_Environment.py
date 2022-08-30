import qmt

import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject


class EnvironmentDavid_thisExample(EnvironmentDavid):

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        print("here comes the controller stuff")

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

    agent1.dynamics.input = [1, 0]

    def print_agent1_state(*args, **kwargs):
        print(f"Agent 1 State: {agent1.dynamics.state}")

    core.scheduling.Action(name="Print Agent", function=print_agent1_state, parent=env.scheduling.actions['output'])

    env.init(calltree=False)

    env.start()


if __name__ == '__main__':
    main()
