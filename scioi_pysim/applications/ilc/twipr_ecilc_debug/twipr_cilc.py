from operator import attrgetter
import scioi_pysim.core as core
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ilc as twipr_ilc
import scioi_pysim.applications.ilc.ilc as ilc
import scioi_pysim.applications.ilc.twipr_ecilc_debug.twipr_ecilc as twipr_ecilc


class TWIPR_2D_CILC_Agent(twipr_ecilc.TWIPR_2D_ECILC_Agent):
    def __init__(self, config: dict, poles=None, x0=None, ref=twipr_ilc.ref_default, name=None):
        super().__init__(config=config, poles=poles, x0=x0, ref=ref, name=name)

    def performance_function(self, *args, **kwargs):
        self.performance = 1 / self.ilc.e_norm[-1]

    def update_function(self, agents):
        if not self.active:
            return
        other_agents = twipr_ecilc.get_active_agents(agents)
        best_performer = max(other_agents, key=attrgetter('performance'))
        self.ilc_update(best_performer.ilc.trials[-1].u, best_performer.ilc.trials[-1].e)
