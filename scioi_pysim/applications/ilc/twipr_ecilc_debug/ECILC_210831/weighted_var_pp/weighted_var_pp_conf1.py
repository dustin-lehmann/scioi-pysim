from operator import attrgetter

import random

import numpy as np
import matplotlib.pyplot as plt
import scioi_pysim.core as core
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc
import scioi_pysim.applications.ilc.ilc as ilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ecilc as twipr_ecilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_cilc as twipr_cilc


def performance_function_1(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent):
    if agent.active:
        agent.performance = 1 / agent.ilc.trials[-1].e_norm


def update_function_1(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent, agents):
    if not agent.active:
        return
    other_agents = twipr_ecilc.get_active_agents(agents)
    performances = [a.performance for a in other_agents]
    sum_performances = sum(performances)

    u_cons = agent.ilc.trials[-1].u * 0
    e_cons = agent.ilc.trials[-1].e * 0

    for a in other_agents:
        u_cons = u_cons + a.performance / sum_performances * a.ilc.trials[-1].u
        e_cons = e_cons + a.performance / sum_performances * a.ilc.trials[-1].e

    alpha = (agent.performance / sum_performances)

    agent.ilc_update(alpha * agent.ilc.trials[-1].u + (1 - alpha) * u_cons,
                     alpha * agent.ilc.trials[-1].e + (1 - alpha) * e_cons)


# ------------------------------------------------------------------------------------------------
# Configs

num_trials = 30

config_1 = twipr_ilc.config_1 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}
config_2 = twipr_ilc.config_2 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}
config_3 = twipr_ilc.config_3 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}

# ------------------------------------------------------------------------------------------------
# Baseline
agent1_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_1, name='bl_1')
agent2_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_2, name='bl_2')
agent3_baseline = twipr_ilc.TWIPR_2D_ILC_Agent(config_3, name='bl_3')

agents_baseline = [agent1_baseline, agent2_baseline, agent3_baseline]

for i in range(0, num_trials):
    for agent in agents_baseline:
        agent.simulate_trial(update=True)

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
# ECILC

agent1 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_1, name='1')
agent2 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_2, name='2')
agent3 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_3, name='3')

agents = [agent1, agent2, agent3]

agent1.pts = core.simulation.Timeseries()
agent1.wts = core.simulation.Timeseries()
agent2.pts = core.simulation.Timeseries()
agent2.wts = core.simulation.Timeseries()

agent1.alpha = core.simulation.Timeseries()
agent2.alpha = core.simulation.Timeseries()

for _ in range(0, num_trials):
    for agent in agents:
        agent.simulate_trial(update=False)
    for agent in agents:
        agent.performance_function(agent)
    for agent in agents:
        agent.update_function(agent, agents)

enorm_ecilc = core.simulation.Timeseries(
    ilc.minimum_error_norm(agent1.ilc.e_norm, agent2.ilc.e_norm, agent3.ilc.e_norm))

a = 2
fig, ax = plt.subplots()
plt.plot(agent1_baseline.ilc.e_norm, label='Agent 1 (individual)', color='bisque', **twipr_ilc.e_norm_plot_options)
plt.plot(agent1.ilc.e_norm, label='Agent 1 (GCILC)', color='darkorange', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2_baseline.ilc.e_norm, label='Agent 2 (individual)', color='lightgreen', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2.ilc.e_norm, label='Agent 2 (GCILC)', color='darkgreen', **twipr_ilc.e_norm_plot_options)
plt.plot(agent3_baseline.ilc.e_norm, label='Agent 3 (individual)', color='lightblue', **twipr_ilc.e_norm_plot_options)
plt.plot(agent3.ilc.e_norm, label='Agent 3 (GCILC)', color='darkblue', **twipr_ilc.e_norm_plot_options)

plt.plot(enorm_ecilc, label='GCILC', color='red')
plt.plot(enorm_cilc, label='CILC', color='black')
plt.xlabel("Trial $j$")
plt.ylabel("Error norm $||e||$")
# plt.legend(loc='center left',  bbox_to_anchor=(1, 0.5))
plt.xticks(ticks=agent1.ilc.e_norm.t)
plt.yscale('log')
plt.ylim(bottom=0.5, top=10)
plt.grid(True, which="both", ls="-")
plt.legend(loc='upper right')
core.utils.xtick_labels_hide(ax, 5)
plt.show()
