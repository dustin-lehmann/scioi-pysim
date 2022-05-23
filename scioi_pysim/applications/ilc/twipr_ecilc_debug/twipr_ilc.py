import numpy as np
from math import pi

import scioi_pysim.core as core
import scioi_pysim.applications.ilc.ilc as ilc
import scioi_pysim.dynamics.twipr as twipr

e_norm_plot_options = {'linestyle': ':', 'marker': 'o'}

Ts = 0.02
poles_default = [0, -20, -3 + 1j, -3 - 1j]

config_1 = {'method': 'q', 'r': 0.01, 's': 3}
config_2 = {'method': 'q', 'r': 0.2, 's': 0.4}
config_3 = {'method': 'pd', 'p': -1.25, 'd': 1.6}

config_4 = {'method': 'pd', 'p': -1, 'd': 1}

config_5 = {'method': 'q', 'r': 0.1, 's': 0.1}

ref_default = core.simulation.Timeseries(list(np.hstack(
    (np.zeros(7), 1.31 * np.sin(4 / 3 * pi * 0.02 * np.arange(0, 20)), 1.31 + 0 * np.arange(20, 36),
     1.31 * np.sin(8 / 3 * 0.02 * pi * (np.arange(36, 46) - 26)),
     0.98 * np.sin(8 / 3 * 0.02 * pi * (np.arange(46, 55) - 26)), -0.98 + 0 * np.arange(55, 80)))))

x0_default = [0, 0, 0, 0]


class TWIPR_2D_ILC_Agent(ilc.ILC_Agent):

    def __init__(self, config: dict, poles=None, x0=None, ref=ref_default, name=None):
        if poles is None:
            poles = poles_default
        if x0 is None:
            x0 = x0_default

        # super(TWIPR_2D_ILC_Agent, self).__init__(
        #     dynamics=twipr.TWIPR_2D_Linear(model=twipr.ModelMichael, Ts=Ts, poles=poles),
        #     ilc={'x0': x0, 'ref': ref}, name=name)

        super(TWIPR_2D_ILC_Agent, self).__init__(
            dynamics=twipr.TWIPR_2D_Linear(model=twipr.ModelMichael, Ts=Ts, poles=poles),
            ilc={'x0': x0, 'ref': ref}, name=name)

        if config['method'] == 'q':
            self.ilc.qlearning(config['r'], config['s'])
        elif config['method'] == 'pd':
            self.ilc.pdlearning(config['p'], config['d'])
