from math import pi

from matplotlib import pyplot as plt

from applications.PPA_Foraging.environment.environments.ppa_foraging_environment_simple import EnvironmentSimple
from applications.PPA_Foraging.environment.ppa_foraging_definitions import Robot_Base
from applications.PPA_Foraging.environment.ppa_foraging_environment import EnvironmentBase
from scioi_py_core.core.spaces import ScalarDimension

from scioi_py_core.objects.world.grid import Grid2D

import logging
# logging.basicConfig(level=logging.INFO)

def main():
    env = EnvironmentBase(visualization='babylon')
    grid = Grid2D(env.world, cell_size=0.5, cells_x=10, cells_y=10, origin=[0,0])
    agent1 = Robot_Base(agent_id=0, name='Agent1', world=env.world)
    agent1.setPosition(y=-1)

    agent2 = Robot_Base(agent_id=0, name='Agent2', world=env.world)
    agent2.setPosition(y=0.5)
    agent2.setConfiguration(dimension='psi', value=pi)

    last_cell_agent1 = grid.getCell(pos_x=agent1.configuration['pos']['x'], pos_y=agent1.configuration['pos']['y'])
    last_cell_agent2 = grid.getCell(pos_x=agent2.configuration['pos']['x'], pos_y=agent2.configuration['pos']['y'])

    def mark_cells():
        print("gfdhjf")
        nonlocal last_cell_agent1, last_cell_agent2
        current_cell_agent1 = grid.getCell(pos_x=agent1.configuration['pos']['x'], pos_y=agent1.configuration['pos']['y'])
        if current_cell_agent1 != last_cell_agent1:
            last_cell_agent1.highlight(False)
            current_cell_agent1.highlight(True, color=[1,0,0])
            last_cell_agent1 = current_cell_agent1

        current_cell_agent2 = grid.getCell(pos_x=agent2.configuration['pos']['x'], pos_y=agent2.configuration['pos']['y'])
        if current_cell_agent2 != last_cell_agent2:
            last_cell_agent2.highlight(False)
            current_cell_agent2.highlight(True, color=[0,1,0])
            last_cell_agent2 = current_cell_agent2

    # env.scheduling.actions['output'].registerAction(action=mark_cells)

    agent1.dynamics.input = [0.5, 0.5]
    agent2.dynamics.input = [0.25, 0.5]

    env.init()
    env.start()



if __name__ == '__main__':
    main()