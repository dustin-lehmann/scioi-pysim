import matplotlib.pyplot as plt
import scioi_pysim.core as core
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc

agent1 = twipr_ilc.TWIPR_2D_ILC_Agent(twipr_ilc.config_1)
agent2 = twipr_ilc.TWIPR_2D_ILC_Agent(twipr_ilc.config_2)
agent3 = twipr_ilc.TWIPR_2D_ILC_Agent(twipr_ilc.config_3)

for _ in range(0, 25):
    agent1.simulate_trial(update=True)
    agent2.simulate_trial(update=True)
    agent3.simulate_trial(update=True)


plt.plot(agent1.ilc.e_norm, label='Agent 1', color='red', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2.ilc.e_norm, label='Agent 2', color='green', **twipr_ilc.e_norm_plot_options)
plt.plot(agent3.ilc.e_norm, label='Agent 3', color='blue', **twipr_ilc.e_norm_plot_options)
plt.grid()
plt.legend()
plt.show()

a = 2