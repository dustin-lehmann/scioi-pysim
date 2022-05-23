# from p11_sim_framework.core import Dimension, StateSpace, SpaceMapping, World, Agent, Dynamics, Obstacle

import scioi_pysim.core as core

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

# State and Configuration Space for all Objects
xyp_ss = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name='x'), core.spaces.Dimension(name='y'), core.spaces.Dimension(name='psi')])

xyp_cs = core.spaces.StateSpace(dimensions = [core.spaces.Dimension(name='x'), core.spaces.Dimension(name='y'), core.spaces.Dimension(name='psi')])

core.spaces.SpaceMapping(xyp_ss, xyp_cs, mapping=lambda state: [state['x'], state['y'], state['psi']],
             inverse=lambda state: [state['x'], state['y'], state['psi']])

xyp_si_input_space = core.spaces.StateSpace(dimensions=[core.spaces.Dimension('v'), core.spaces.Dimension('psi_dot')])


# ----------------------------------------------------------------------------------------------------------------------

# XYP-Dynamics
class XYP_Single_Integrator_Dynamics(core.dynamics.Dynamics):
    def __init__(self):
        super().__init__(state_space=xyp_ss, config={'n': 3, 'p': 2, 'q': 3}, input_space=xyp_si_input_space,
                         output_space=xyp_ss)

    def meas(self, state):
        return state

    def dynamics(self, state, u):
        # liegt hier der fehler?
        # sollte folgendes: 2 inputs: Geschw. v und psi_dot?
        # 3 outputs: [x, y, psi]

        x = state + u
        y = self.meas(state)
        return x, y


# ----------------------------------------------------------------------------------------------------------------------

# XYP-Agents
class XYP_Agent(core.agents.Agent):

    def __init__(self, name=None, state=None):
        super().__init__(name=name, config_space=xyp_cs, dynamics=XYP_Single_Integrator_Dynamics(), state=state)


# ----------------------------------------------------------------------------------------------------------------------


# XYP-World
class XYP_World(core.world.World):
    def __init__(self):
        super().__init__(configuration_space=xyp_cs, agent_sim_mode="parallel")


# ----------------------------------------------------------------------------------------------------------------------


# XYP-Plot
class XYP_Plot:

    def __init__(self, world):
        self.world = world

    def update(self, Agent, Mode, LastStep=False, stateLog=[], Obstacle=None):

        print('Plot updating')

        # start plot here
        if Mode == "rt":
            pass
        elif Mode == "fast" and LastStep:

            for i in range(0, len(Agent)):
                for j in range(0, len(Agent[i].log)):
                    print(f'configuration: {Agent[i].log[j].config}')
                    print(f'Dynamic Input: {Agent[i].log[j].dynamic_input}')
                    stateLog.append(Agent[i].log[j].config)
            log_arr = np.squeeze(np.array(stateLog))

            print(f'length Agent: {len(Agent)}')
            print(f'type of Agent: {type(Agent)}')
            print(f'Agent: {Agent}')
            print(stateLog)
            print(type(stateLog))
            print(f'log_arr = {log_arr}')
            print(type(log_arr))
            print(log_arr.shape)
            print(len(Agent[i].log))

            fig = plt.figure("Fast Plot")

            color = iter(cm.rainbow(np.linspace(0, 1, int(len(Agent)))))

            for k in range(0, int(len(Agent))):
                c = next(color)
                x = log_arr[k * len(Agent[i].log):(k + 1) * len(Agent[i].log), 0]
                y = log_arr[k * len(Agent[i].log):(k + 1) * len(Agent[i].log), 1]
                # get psi from log as orientation?
                plt.quiver(x[:-1], y[:-1], x[1:] - x[:-1], y[1:] - y[:-1], color=c, scale_units='xy', angles='xy',
                           scale=1)

            plt.axis([-20, 20, -20, 20])
            plt.grid(b='true', axis='both')

            plt.xlabel("x coordinate")
            plt.ylabel("y coordinate")
            plt.title("Trajectory of the agents")
            # plt.xlim([-15, 15])
            # plt.ylim([-15, 15])

            plt.draw()
            plt.show()
