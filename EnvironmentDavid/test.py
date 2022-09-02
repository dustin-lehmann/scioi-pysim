import logging
import math

from scioi_py_core import core as core

from Objects import EnvironmentDavid_World, EnvironmentDavid_Dynamics, EnvironmentDavid_Agents

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  %(levelname)-8s  %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def main():
    world = EnvironmentDavid_World.DynamicWorld_XYZR_Simple(name='Testworld')

    agent1 = EnvironmentDavid_Agents.TankRobotSimObject(name='Agent 1', world=world)
    agent2 = EnvironmentDavid_Agents.TankRobotSimObject(name='Agent 2', world=world)

    agent1.dynamics.input = [1, 1]
    agent2.dynamics.input = [3, -1]

    for i in range(0, 30):
        world.scheduling.actions['dynamics']()
        world.scheduling.actions['physics_update']()
        print(agent1.dynamics.state)
        print(agent2.dynamics.state)

    # print(agent1.physics.collision(agent2.physics))
    #
    core.physics.PhysicsDebugPlot(representations=[agent1.physics, agent2.physics], limits={'x': [-1, 1], 'y': [-1, 1]})


if __name__ == '__main__':
    main()
