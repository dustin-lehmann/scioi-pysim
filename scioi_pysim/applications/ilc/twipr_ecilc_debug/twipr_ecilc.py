import scioi_pysim.applications.ilc.ilc as ilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc


class TWIPR_2D_ECILC_Agent(twipr_ilc.TWIPR_2D_ILC_Agent):

    def __init__(self, config: dict, poles=None, x0=None, ref=twipr_ilc.ref_default, name=None):
        self.ecilc_data = {'entry_trial': 0,
                           'performance_function': None,
                           'update_function': None}

        self.weight = 0
        self.performance = 0
        self.active = False

        for key, value in config.items():
            if key in self.ecilc_data:
                self.ecilc_data[key] = config[key]

        super(TWIPR_2D_ECILC_Agent, self).__init__(config=config, poles=poles, x0=x0, ref=ref, name=name)

    def simulate_trial(self, update=False, append=True, u=None):
        if self.sim.step >= self.ecilc_data['entry_trial']:
            self.active = True

        if self.active:
            x, y, e, u = super().simulate_trial(update, append, u)
            return x, y, e, u
        else:
            if append:
                self.ilc.trials.append(ilc.ILC_Trial(None, None, self.ilc.u0, None, self.ilc.ref))
                return None

    # ------------------------------------------------------------------------------------------------------------------
    def ecilc_update_step_1(self, agents):
        self.ecilc_data['step_1_function'](self, agents)

    def ecilc_update_step_2(self, agents):
        self.ecilc_data['step_2_function'](self, agents)

    def performance_function(self, *args, **kwargs):
        if not self.active:
            return
        self.ecilc_data['performance_function'](*args, **kwargs)

    def update_function(self, *args, **kwargs):
        if not self.active:
            return
        self.ecilc_data['update_function'](*args, **kwargs)


def get_active_agents(agents: list[TWIPR_2D_ECILC_Agent]):
    return [agent for agent in agents if agent.active]
