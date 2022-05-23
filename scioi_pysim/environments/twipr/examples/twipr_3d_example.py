import scioi_pysim.core.simulator as simulator
from scioi_pysim.environments.twipr.robots.twipr3D import TWIPR_3D_Agent_SCTRL, TWIPR_3D_World, \
    TWIPR_3D_CTRL_MODE

Ts = 0.01

world = TWIPR_3D_World(Ts=Ts)
twipr = TWIPR_3D_Agent_SCTRL(Ts=Ts, world=world)

sim = simulator.Simulator(mode='fast', Ts=Ts, objects=world)

twipr.controller.set_mode(TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SC)


def user_input(*args, **kwargs):
    twipr.external_input = [0.2, 0]


def user_output(*args, **kwargs):
    # print(twipr.state)
    pass


sim.user_input = user_input
sim.user_output = user_output

sim.init()


sim.run(time=20)

a = 2