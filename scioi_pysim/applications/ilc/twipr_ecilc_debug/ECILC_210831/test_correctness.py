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

    agent.ilc_update(u_cons, e_cons)

    if len(agent.ilc.trials) > 2:
        a = 3


num_trials = 30

config_1 = twipr_ilc.config_1 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}
config_2 = twipr_ilc.config_2 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}
config_3 = twipr_ilc.config_3 | {'entry_trial': 0, 'performance_function': performance_function_1,
                                 'update_function': update_function_1}

agent1 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_1, name='1')
agent2 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_2, name='2')

agents = [agent1, agent2]

for _ in range(0, num_trials):
    for agent in agents:
        agent.simulate_trial(update=False)
    for agent in agents:
        agent.performance_function(agent)
    for agent in agents:
        agent.update_function(agent, agents)

enorm_ecilc = ilc.minimum_error_norm(agent1.ilc.e_norm, agent2.ilc.e_norm)

plt.plot(agent1.ilc.e_norm, label='Agent 1', color='orange', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2.ilc.e_norm, label='Agent 2', color='green', **twipr_ilc.e_norm_plot_options)

plt.plot(enorm_ecilc, label='ECILC', color='red')
plt.xlabel("Trial $j$")
plt.ylabel("Error norm $||e||$")
plt.xticks(ticks=agent1.ilc.e_norm.t)
plt.yscale('log')
plt.ylim(bottom=0.5, top=10)
plt.grid(True, which="both", ls="-")
plt.legend()
plt.show()
