import numpy as np
import dataclasses
from typing import List, Union

import scioi_pysim.core as core

# ILC_Trial ############################################################################################################
import scioi_pysim.lib_control


class ILC_Trial:
    e: core.simulation.Timeseries
    u: core.simulation.Timeseries
    y: core.simulation.Timeseries
    x: core.simulation.Timeseries
    ref: core.simulation.Timeseries

    # == INIT ==========================================================================================================
    def __init__(self, x, y, u, e, ref):
        self.x = x
        self.y = y
        self.u = u
        self.e = e
        self.ref = ref

    # == PROPERTIES ====================================================================================================
    @property
    def e_norm(self):
        if self.e is None:
            return None
        else:
            return np.linalg.norm(self.e)

    # == PRIVATE METHODS ===============================================================================================
    def __repr__(self):
        return "norm(e): {:.2f}, len: {:d}".format(self.e_norm, len(self.e))


# ILC_Data #############################################################################################################
@dataclasses.dataclass
class ILC_Data:
    P: np.ndarray = None
    _ref: core.simulation.Timeseries = None
    m: int = None

    _method: str = None  # 'no' or 'pd'
    _params: tuple = None  # (r,s) or (kp,kd)

    L: np.ndarray = None
    Q: np.ndarray = None

    u: core.simulation.Timeseries = None
    u0: core.simulation.Timeseries = None
    x0: core.spaces.State = None

    trials: List[ILC_Trial] = dataclasses.field(default_factory=list)
    dynamics: core.dynamics.LinearDynamics = None

    # == PROPERTIES ====================================================================================================
    @property
    def N(self):
        return len(self.ref)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        assert (isinstance(value, (list, core.simulation.Timeseries)))
        if isinstance(value, list):
            value = core.simulation.Timeseries(value)

        self._ref = value
        self.m = scioi_pysim.lib_control.relative_degree(self.dynamics.sys)
        self.u0 = core.simulation.Timeseries([np.zeros(self.dynamics.p)] * self.N)
        self.P = scioi_pysim.lib_control.calc_transition_matrix(self.dynamics.sys, self.N)

        if self.params is not None:
            self.set_learning(self.method, self.params)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value
        if self.params is not None:
            self.set_learning(self.method, self.params)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value
        if self.method is not None:
            self.set_learning(self.method, self.params)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def e_norm(self):
        if len(self.trials) > 0:
            return core.simulation.Timeseries([trial.e_norm for trial in self.trials])

    # == METHODS =======================================================================================================
    def qlearning(self, r, s):
        self.Q, self.L = scioi_pysim.lib_control.qlearning(self.P, 1, r, s)

    def pdlearning(self, kp, kd):
        self.L = scioi_pysim.lib_control.pdlearning(kp, kd, self.N)
        self.Q = np.eye(self.N)

    # == METHODS =======================================================================================================
    def set_learning(self, method, params):
        if method == 'no':
            self.qlearning(r=params[0], s=params[1])
        elif method =='pd':
            self.pdlearning(kp=params[0], kd=params[1])

# ILC_Agent ############################################################################################################
class ILC_Agent(core.agents.DynamicAgent):
    ilc: ILC_Data
    state_0: core.spaces.State
    ref: core.simulation.Timeseries

    # == INIT ==========================================================================================================
    def __init__(self, dynamics: core.dynamics.Dynamics, ilc_dynamics: core.dynamics.Dynamics = None,
                 ilc_config: dict = None, name: str = None, Ts: float = 1, state_0: core.spaces.State = None,
                 ref: core.simulation.Timeseries = None, **kwargs):

        super().__init__(dynamics=dynamics, name=name, Ts=Ts, **kwargs)

        if ilc_dynamics is None:
            if isinstance(dynamics, core.dynamics.LinearDynamics):
                ilc_dynamics = dynamics
            elif hasattr(dynamics, 'linear_dynamics'):
                ilc_dynamics = dynamics.linear_dynamics
            else:
                raise Exception

        self.ilc = ILC_Data()
        self.ilc.dynamics = ilc_dynamics
        if ilc_config is not None:
            core.utils.dict_to_dataclass(ilc_config, self.ilc)

        if state_0 is not None:
            self.ilc.x0 = state_0

        if ref is not None:
            self.ilc.ref = ref

            # TODO: SIM PHASES


    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================
    def update(self, input=None, phase=None):
        super().update(input=input, phase=phase)

    # ------------------------------------------------------------------------------------------------------------------
    def simulate_trial(self, update=False, append=True, u=None):
        assert (self.ilc.x0 is not None)

        if self.ilc.u is None:
            self.ilc.u = self.ilc.u0

        if u is None:
            u = self.ilc.u

        u_ext = u.append([np.zeros(self.dynamics.p) for _ in range(0, self.ilc.m)], copy=True)

        # run a simulation
        x, y, _ = self.simulate(input=u_ext, x0=self.ilc.x0, t0=False)

        y = core.simulation.Timeseries(y[self.ilc.m:], Ts=self.dynamics.Ts)
        e = core.simulation.Timeseries(self.ilc.ref - y, name='e',Ts=self.dynamics.Ts)

        if append:
            self.ilc.trials.append(ILC_Trial(x, y, self.ilc.u, e, self.ilc.ref))

        if update:
            self.ilc_update()

        return x, y, e, self.ilc.u
    # ------------------------------------------------------------------------------------------------------------------
    def ilc_update(self, u=None, e=None, *args, **kwargs):
        if self.ilc.L is None or self.ilc.Q is None:
            raise Exception("ILC learning functions not set!")

        if u is None:
            u = self.ilc.trials[-1].u
        if e is None:
            e = self.ilc.trials[-1].e

        self.ilc.u = scioi_pysim.lib_control.ilc_update(self.ilc.Q, self.ilc.L, u, e)

    # ------------------------------------------------------------------------------------------------------------------
    def reset_learning(self):
        self._reset()


    # == PRIVATE METHODS ===============================================================================================
    def _reset(self):
        super()._reset()
        self.ilc.trials = []
        self.ilc.u = None


def minimum_error_norm(*args):
    len1 = len(args[0])
    assert(len(arg) == len1 for arg in args)

    enorm = []

    for i in range(0, len1):
        e = []
        for j, arg in enumerate(args):
            e.append(arg[i])
        enorm.append(min(e))

    return enorm
