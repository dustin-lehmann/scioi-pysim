from operator import attrgetter

import matplotlib.pyplot as plt
import scioi_pysim.core as core
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ecilc as twipr_ecilc


def test_fun_1(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent, agents):
    if agent.active:
        agent.weight = 1 / agent.ilc.trials[-1].e_norm


def test_fun_2(agent: twipr_ecilc.TWIPR_2D_ECILC_Agent, agents):
    if not agent.active:
        return
    other_agents = twipr_ecilc.get_active_agents(agents)
    weights = [a.weight for a in other_agents]
    sum_weights = sum(weights)
    best_performer = max(other_agents, key=attrgetter('weight'))

    u_cons = agent.ilc.trials[-1].u * 0
    e_cons = agent.ilc.trials[-1].e * 0

    # for a in other_agents:
    #     u_cons = u_cons + a.weight / sum_weights * a.ilc.trials[-1].u
    #     e_cons = e_cons + a.weight / sum_weights * a.ilc.trials[-1].e
    for a in other_agents:
        u_cons = u_cons + 1 / len(other_agents) * a.ilc.trials[-1].u
        e_cons = e_cons + 1 / len(other_agents) * a.ilc.trials[-1].e

    agent.ilc_update(u_cons, e_cons)


config_1 = twipr_ilc.config_1 | {'entry_trial': 0, 'step_1_function': test_fun_1, 'step_2_function': test_fun_2}
config_2 = twipr_ilc.config_2 | {'entry_trial': 0, 'step_1_function': test_fun_1, 'step_2_function': test_fun_2}
config_3 = twipr_ilc.config_3 | {'entry_trial': 0, 'step_1_function': test_fun_1, 'step_2_function': test_fun_2}

agent1 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_1, name='1')
agent2 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_2, name='2')
agent3 = twipr_ecilc.TWIPR_2D_ECILC_Agent(config_3, name='3')

agents = [agent1, agent2, agent3]

for _ in range(0, 30):
    for agent in agents:
        agent.simulate_trial(update=False)
    for agent in agents:
        agent.ecilc_update_step_1(agents)
    for agent in agents:
        agent.ecilc_update_step_2(agents)

plt.plot(agent1.ilc.e_norm, label='Agent 1', color='red', **twipr_ilc.e_norm_plot_options)
plt.plot(agent2.ilc.e_norm, label='Agent 2', color='green', **twipr_ilc.e_norm_plot_options)
plt.plot(agent3.ilc.e_norm, label='Agent 3', color='blue', **twipr_ilc.e_norm_plot_options)
plt.xlabel("Trial $j$")
plt.title("Approach 3: Average CILC")
plt.ylabel("Error norm $||e||$")
plt.xticks(ticks=agent1.ilc.e_norm.t)
plt.yscale('log')
plt.ylim(bottom=0.5, top=10)
plt.grid(True, which="both", ls="-")
plt.legend()
plt.show()
