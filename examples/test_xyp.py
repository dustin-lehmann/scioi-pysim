import random



from scioi_pysim.applications.world_xyp import XYP_World, XYP_Agent, XYP_Single_Integrator_Dynamics, XYP_Plot
from p11_sim_framework import Simulator, Function, Sensor

# ---------------------------------------------------------------------------------------------------------------------

#   TO-DO Vision Sensor:
#   - was sind meine Messgrößen und was gebe ich aus?
#       + für jeden Agenten im Sichtfeld
#           - ID / name
#           - relative Position c_rel
#   - Was sind meine Parameter?
#       + Field_of_View (FoV)
#       + Uncertainty von c_rel in abhängigkeit vom Abstand
#       + Uncertainty von rel. Position in (FoV) --> Am Rand des FoV höhere Unsicherheit, da Verzerrung am stärksten
#   - Wie sage ich dem programm, dass sich ein oder mehrere agenten in meinem FoV befinden?


class VisionSensor(Sensor):
    def measure(self):
        # platzhalter: verteile random values zw -agent.id und + agent.id
        self.value = random.randint(-self.agent.id, self.agent.id)
        self.log['value'] = self.value

        # hier muss sensor implementiert werden

# ----------------------------------------------------------------------------------------------------------------------


class TestAgent(XYP_Agent):
    def __init__(self, state=None):
        super().__init__(state=state)
        self.sensors['sensor1'] = VisionSensor(agent=self)

    def input_fun(self):
        self.sensors['sensor1'].measure()
        # print(self.sensors['sensor1'].value)

    def logic_fun(self):
        # was ist mein dynamic_input? siehe dynamics.py class Dynamics
        # was muss ich übergeben? input sollte [v, psi_dot] sein
        self.dynamic_input = [-self.sensors['sensor1'].value + 1, self.sensors['sensor1'].value + 1]


    def comm1_fun(self):
        pass

    def comm2_fun(self):
        pass

    def post_fun(self):
        pass

# ---------------------------------------------------------------------------------------------------------------------


class TestWorld(XYP_World):
    def __init__(self):
        super().__init__()

    def input_fun(self):
        pass

    def logic_fun(self):
        pass

    def network_fun(self):
        pass

    def post_fun(self):
        pass

    def environment_fun(self):
        pass


# ---------------------------------------------------------------------------
# def update_plot():
#      plot.update(Agent=agents, Mode=simMode, LastStep=sim.t + sim.dt == simTime)

# ---------------------------------------------------------------------------

# World
world = TestWorld()
agents = [TestAgent(state=[0, 0, 0])]
world.add_agent(agents)

# Plotting
# still needs to be implemented
# plot = XYP_Plot(world)


# Simulator
simMode = 'fast'
simTime = 20
sim = Simulator(mode=simMode, dt=1, world=world)
# sim.phases['output'].add_function(Function(update_plot))

sim.simulate(time=simTime)

for agent in agents:
    print("Agent {:d}: x: {:.1f}({:.1f}) y: {:.1f}({:.1f})".format(agent.id, agent.config[0], agent.state[0],
                                                                   agent.config[1], agent.state[1]))