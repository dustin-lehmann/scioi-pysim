from operator import attrgetter

import random

import numpy as np
import matplotlib.pyplot as plt
import scioi_pysim.core as core
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc
import scioi_pysim.applications.ilc.ilc as ilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ecilc as twipr_ecilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_cilc as twipr_cilc


def performance_function_2(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent):
    if agent.active:
        agent.performance = np.zeros(len(agent.ilc.ref))
        for k in range(0, len(agent.performance)):
            error = agent.ilc.trials[-1].e[k]
            if isinstance(error, core.spaces.State):
                error = abs(error.val)

            error = abs(error)

            if error < 1e-5:
                agent.performance[k] = 1000
            else:
                agent.performance[k] = 1 / error


def update_function_2(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent, agents):
    agents = twipr_ecilc.get_active_agents(agents)

    u_cons = agent.ilc.trials[-1].u * 0
    e_cons = agent.ilc.trials[-1].e * 0
    for k in range(len(agent.ilc.ref)):
        sum_performances = sum([a.performance[k] for a in agents])
        for a in agents:
            u_cons[k] = u_cons[k] + a.performance[k] / sum_performances * a.ilc.trials[-1].u[k]
            e_cons[k] = e_cons[k] + a.performance[k] / sum_performances * a.ilc.trials[-1].e[k]

    agent.ilc_update(u_cons, e_cons)

    if len(agent.ilc.trials) > 2:
        a = 3

# ------------------------------------------------------------------------------------------------
# Configs

num_trials = 30

config_1 = twipr_ilc.config_1 | {'entry_trial': 0, 'performance_function': performance_function_2,
                                 'update_function': update_function_2}
config_2 = twipr_ilc.config_2 | {'entry_trial': 0, 'performance_function': performance_function_2,
                                 'update_function': update_function_2}
config_3 = twipr_ilc.config_3 | {'entry_trial': 0, 'performance_function': performance_function_2,
                                 'update_function': update_function_2}

# ------------------------------------------------------------------------------------------------
# Baseline
agent1_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_1, name='bl_1')
agent2_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_2, name='bl_2')
agent3_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_3, name='bl_3')

u01 = core.simulation.Timeseries()
u02 = core.simulation.Timeseries()
u03 = core.simulation.Timeseries()
for i in range(0, len(agent1_baseline.ilc.ref)):
    u01.append(random.uniform(-1, 1))
    u02.append(random.uniform(-1, 1))
    u03.append(random.uniform(-1, 1))

agent1_baseline.ilc.u = u01
agent2_baseline.ilc.u = u02
agent3_baseline.ilc.u = u03

agents_baseline = [agent1_baseline, agent2_baseline, agent3_baseline]

for i in range(0, num_trials):
    for agent in agents_baseline:
        agent.simulate_trial(update=True)
        a = 2

# ------------------------------------------------------------------------------------------------
# CILC
agent1_cilc = twipr_cilc.TWIPR_2D_CILC_Agent(config_1, name='cilc_1')
agent2_cilc = twipr_cilc.TWIPR_2D_CILC_Agent(config_2, name='cilc_1')
agent3_cilc = twipr_cilc.TWIPR_2D_CILC_Agent(config_3, name='cilc_1')

agents_cilc = [agent1_cilc, agent2_cilc, agent3_cilc]

for i in range(0, num_trials):
    for agent in agents_cilc:
        agent.simulate_trial(update=False)
    for agent in agents_cilc:
        agent.performance_function()
    for agent in agents_cilc:
        agent.update_function(agents_cilc)

enorm_cilc = ilc.minimum_error_norm(agent1_cilc.ilc.e_norm, agent2_cilc.ilc.e_norm, agent3_cilc.ilc.e_norm)

# ------------------------------------------------------------------------------------------------

agent1 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_1, name='1')
agent2 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_2, name='2')
agent3 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_3, name='3')

agents = [agent1, agent2, agent3]

for _ in range(0, num_trials):
    for agent in agents:
        agent.simulate_trial(update=False)
    for agent in agents:
        agent.performance_function(agent)
    for agent in agents:
        agent.update_function(agent, agents)

enorm_ecilc = ilc.minimum_error_norm(agent1.ilc.e_norm, agent2.ilc.e_norm, agent3.ilc.e_norm)

a = 2

plt.plot(agent1_baseline.ilc.e_norm, label='Agent 1', color='orange', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2_baseline.ilc.e_norm, label='Agent 2', color='green', **twipr_ilc.e_norm_plot_options)
plt.plot(agent3_baseline.ilc.e_norm, label='Agent 3', color='blue', **twipr_ilc.e_norm_plot_options)

plt.plot(enorm_ecilc, label='ECILC', color='red')
plt.plot(enorm_cilc, label='CILC', color='black')
plt.xlabel("Trial $j$")
plt.ylabel("Error norm $||e||$")
plt.xticks(ticks=agent1.ilc.e_norm.t)
plt.yscale('log')
plt.ylim(bottom=0.5, top=10)
plt.grid(True, which="both", ls="-")
plt.legend()
plt.show()
