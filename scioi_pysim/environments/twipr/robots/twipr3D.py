from math import pi as pi
from numpy import nan as nan
import numpy as np
from enum import Enum

import scioi_pysim.core as core
import scioi_pysim.dynamics.twipr as twipr_dynamics
import scioi_pysim.lib_control as lib_control

TWIPR_3D_ConfigSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x'),
                                                          core.spaces.Dimension(name='y'),
                                                          core.spaces.Dimension(name='theta', limits=[-pi, pi],
                                                                                wrapping=True),
                                                          core.spaces.Dimension(name='psi', limits=[0, 2 * pi],
                                                                                wrapping=True)])

TWIPR_3D_World_CoordinateSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x'),
                                                                    core.spaces.Dimension(name='y'),
                                                                    core.spaces.Dimension(name='z')])

TWIPR_3D_World_ConfigSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x'),
                                                                core.spaces.Dimension(name='y'),
                                                                core.spaces.Dimension(name='z'),
                                                                core.spaces.Dimension(name='theta', limits=[-pi, pi],
                                                                                      wrapping=True),
                                                                core.spaces.Dimension(name='phi', limits=[-pi, pi],
                                                                                      wrapping=True),
                                                                core.spaces.Dimension(name='psi', limits=[0, 2 * pi],
                                                                                      wrapping=True)])

TWIPR_3D_World_ConfigSpace.add_mapping(
    core.spaces.SpaceMapping(TWIPR_3D_World_ConfigSpace, TWIPR_3D_World_CoordinateSpace,
                             mapping=lambda config: [config[0], config[1], config[2]], inverse=None))

twipr_dynamics.TWIPR_3D_StateSpace.add_mapping(
    core.spaces.SpaceMapping(twipr_dynamics.TWIPR_3D_StateSpace, TWIPR_3D_ConfigSpace,
                             mapping=lambda state: [state[0], state[1], state[3], state[5]],
                             inverse=lambda config: [config[0], config[1], 0, config[2], 0,
                                                     config[3]]))

TWIPR_3D_ConfigSpace.add_mapping(core.spaces.SpaceMapping(TWIPR_3D_ConfigSpace, TWIPR_3D_World_ConfigSpace,
                                                          mapping=lambda config: [config[0], config[1], config[2], 0,
                                                                                  config[3]],
                                                          inverse=None))

twipr_dynamics.TWIPR_3D_StateSpace.add_mapping(
    core.spaces.SpaceMapping(twipr_dynamics.TWIPR_3D_StateSpace, TWIPR_3D_World_ConfigSpace,
                             mapping=lambda state: [state['x'], state['y'], 0,
                                                    state['theta'], 0, state['psi']],
                             inverse=lambda config: [config['x'], config['y'], 0,
                                                     config['theta'], 0, config['psi'], 0]))

twipr_3d_poles_default = [0, -20, -3 + 1j, -3 - 1j, 0, -1.5]
twipr_3d_ev_default = np.array([[1, nan, nan, nan, 0, nan],
                                [nan, 1, nan, nan, nan, nan],
                                [nan, nan, 1, 1, nan, 0],
                                [nan, nan, nan, nan, nan, nan],
                                [0, nan, nan, nan, 1, 1],
                                [nan, 0, 0, 0, nan, nan]])

twipr_3d_xdot_config_default = {'Kp': -1.534 / 2, 'Ki': -2.81 / 2, 'Kd': -0.07264 / 2, 'max_rate': 50, 'max': None}
twipr_3d_psidot_config_default = {'Kp': -0.3516, 'Ki': -1.288, 'Kd': -0.0002751, 'max_rate': None, 'max': None}
twipr_3d_psi_config_default = {'Kp': -2.202 / 2, 'Ki': -3.269 / 2, 'Kd': -0.3707 / 2, 'max_rate': 2000, 'max': None}

twipr_3d_psi_pid2_config_default = {'Kp': -0.9824 / 2, 'Ki': -1.019 / 2, 'Kd': -0.2369 / 2, 'b': 0.8858,
                                    'c': 0.6566, 'max': 25}


########################################################################################################################
class TWIPR_3D_CTRL_MODE(Enum):
    TWIPR_3D_CTRL_OFF = 0
    TWIPR_3D_CTRL_SF = 1
    TWIPR_3D_CTRL_SC = 2
    TWIPR_3D_CTRL_PC = 3


class TWIPR_3D_CTRL:
    xdot_ctrl: lib_control.PID_ctrl
    psidot_ctrl: lib_control.PID_ctrl
    psi_ctrl: lib_control.PID2_ctrl
    sf_ctrl: np.ndarray

    mode: TWIPR_3D_CTRL_MODE

    start_counter: int

    last_state = None

    def __init__(self, Ts, K: np.ndarray, xdot_config=None, psidot_config=None):

        self.sf_ctrl = K

        if xdot_config is None:
            xdot_config = twipr_3d_xdot_config_default
        self.xdot_config = xdot_config

        if psidot_config is None:
            psidot_config = twipr_3d_psidot_config_default
        self.psidot_config = psidot_config

        psi_config = twipr_3d_psi_pid2_config_default

        self.xdot_ctrl = lib_control.PID_ctrl(Ts=Ts, P=xdot_config["Kp"], I=xdot_config["Ki"], D=xdot_config["Kd"],
                                              max_rate=xdot_config['max_rate'])
        self.psidot_ctrl = lib_control.PID_ctrl(Ts=Ts, P=psidot_config["Kp"], I=psidot_config["Ki"],
                                                D=psidot_config["Kd"])

        # self.psi_ctrl = lib_control.PID_ctrl(Ts=Ts, P=psi_config["Kp"], I=psi_config["Ki"],
        #                                      D=psi_config["Kd"], max_rate=psi_config['max_rate'])

        self.psi_ctrl = lib_control.PID2_ctrl(Ts=Ts, P=psi_config["Kp"], I=psi_config["Ki"],
                                              D=psi_config["Kd"], b=psi_config['b'], c=psi_config['c'],
                                              max=psi_config['max'])

        self.mode = TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_OFF

        self.start_counter = 0
        self.last_psi = None

    def update(self, input, state):

        output = np.array([0, 0])

        if (state['theta'] >= (pi / 2 - 0.001) or state['theta'] <= -(pi / 2 - 0.001)) and self.start_counter == 0:
            self.mode = TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_OFF

        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SF or self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SC or \
                self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_PC:
            output = -self.sf_ctrl @ state

        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_PC:
            e_xdot = input[0] - state['v']

            if self.last_psi is None:
                self.last_psi = state['psi']

            arr = np.unwrap(np.array([self.last_psi, state['psi'], input[1]]))
            psi = arr[1]
            ref = arr[2]

            self.last_psi = psi

            u_xdot = self.xdot_ctrl.update(e_xdot)
            u_psi = self.psi_ctrl.update(ref, psi)

            output = output + np.array([u_xdot + u_psi, u_xdot - u_psi])

        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SC:
            e_xdot = input[0] - state['v']
            e_psidot = input[1] - state['psi_dot']

            u_xdot = self.xdot_ctrl.update(e_xdot)
            u_psidot = self.psidot_ctrl.update(e_psidot)

            output = output + np.array([u_xdot + u_psidot, u_xdot - u_psidot])

        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SF:
            output = output + np.array([input[0] + input[1], input[0] - input[1]])

        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_OFF:
            output = np.array([0, 0])

        if self.start_counter > 0:
            self.start_counter = self.start_counter - 1

        return output

    def set_mode(self, mode: TWIPR_3D_CTRL_MODE):
        if mode == self.mode:
            return

        self.reset()
        if self.mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_OFF and (
                mode == TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SF or TWIPR_3D_CTRL_MODE.TWIPR_3D_CTRL_SC):
            self.start_counter = 20
        self.mode = mode

    def reset(self):
        self.xdot_ctrl.reset()
        self.psidot_ctrl.reset()


########################################################################################################################
twipr_3d_agent_sctrl_external_input_space = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='xdot_cmd'),
                                                                               core.spaces.Dimension(
                                                                                   name='psidot_cmd')])


########################################################################################################################
class TWIPR_3D_Agent_SCTRL(core.agents.DynamicAgent):
    linear_dynamics: twipr_dynamics.TWIPR_3D_Linear
    controller: TWIPR_3D_CTRL

    def __init__(self, Ts, world=None, state=None, name=None, model=twipr_dynamics.ModelMichael, poles=None,
                 ev=twipr_3d_ev_default, xdot_ctrl_config=None, psidot_ctrl_config=None):
        if poles is None:
            self.poles = twipr_3d_poles_default
        else:
            self.poles = poles

        self.ev = ev

        super().__init__(dynamics=twipr_dynamics.TWIPR_3D_Nonlinear(model=model, Ts=Ts, poles=None, ev=None),
                         configuration_space=TWIPR_3D_ConfigSpace,
                         external_input_space=twipr_3d_agent_sctrl_external_input_space,
                         state=state,
                         name=name,
                         world=world,
                         Ts=Ts)

        K = self.dynamics.linear_dynamics.set_eigenstructure(self.poles, self.ev, set=False)

        if K.shape == (2, 6):
            K = np.hstack((np.zeros((self.dynamics.p, 1)), K))

        self.controller = TWIPR_3D_CTRL(Ts=Ts, K=K, xdot_config=xdot_ctrl_config, psidot_config=psidot_ctrl_config)

        self.external_input = self._spaces.external_input_space.zeros()

    # === PRIVATE METHODS ==============================================================================================
    def _action_input(self, *args, **kwargs):
        super()._action_input(*args, **kwargs)

    def _action_sensors(self):
        super()._action_sensors()

    def _action_logic_pre_dyn(self):
        super()._action_logic_pre_dyn()
        self._dynamic_input = self.controller.update(input=self.external_input, state=self.state)

    def _action_logic_post_dyn(self):
        super()._action_logic_post_dyn()

    def _action_post(self):
        super()._action_post()
        self.sim.log_value('state', self.state)


########################################################################################################################
class TWIPR_3D_World(core.world.DynamicWorld):

    def __init__(self, Ts):
        super().__init__(Ts=Ts, coordinate_space=TWIPR_3D_World_CoordinateSpace,
                         configuration_space=TWIPR_3D_World_ConfigSpace)

    def _action_environment(self):
        for agent in self.objects.agents:
            on_ground_pos = False
            on_ground_neg = False

            if agent.state['theta'] >= pi / 2:
                agent.state['theta'] = pi / 2
                on_ground_pos = True
            elif agent.state['theta'] <= -pi / 2:
                agent.state['theta'] = -pi / 2
                on_ground_neg = True

            while agent.state['theta'] > pi:
                agent.state['theta'] = agent.state['theta'] - 2 * pi

            while agent.state['theta'] < -pi:
                agent.state['theta'] = agent.state['theta'] + 2 * pi

            if (on_ground_pos and agent.state['theta_dot'] > 0) or (on_ground_neg and agent.state['theta_dot'] < 0):
                agent.state['theta_dot'] = 0

            if on_ground_pos or on_ground_neg:
                agent.state['v'] = agent.state['v'] * 0.8
                agent.state['psi_dot'] = agent.state['psi_dot'] * 0.8

            # if agent.state['theta'] >= pi / 2:
            #     agent.state['theta'] = pi / 2
            #     on_ground_pos = True
            # elif agent.state['theta'] <= -pi / 2:
            #     agent.state['theta'] = -pi / 2
            #     on_ground_neg = True
            #
            # if (on_ground_pos and agent.state['theta_dot'] > 0) or (on_ground_neg and agent.state['theta_dot'] < 0):
            #      agent.state['theta_dot'] = 0
