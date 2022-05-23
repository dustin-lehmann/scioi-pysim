import numpy as np
import control
from math import pi

from scioi_pysim import core
from scioi_pysim import lib_control


class TwiprModel:
    def __init__(self, m_b, m_w, l, d_w, I_w, I_w2, I_y, I_x, I_z, c_alpha, r_w, tau_theta, tau_x):
        self.m_b = m_b
        self.m_w = m_w
        self.l = l
        self.d_w = d_w
        self.I_w = I_w
        self.I_w2 = I_w2
        self.I_y = I_y
        self.I_x = I_x
        self.I_z = I_z
        self.c_alpha = c_alpha
        self.r_w = r_w
        self.tau_theta = tau_theta
        self.tau_x = tau_x


# ModelMichael = TwiprModel(m_b=2.5, m_w=0.636, l=0.026, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648,
# I_x=0.02, I_z=0.03, c_alpha=4.6302e-4, r_w=0.055, tau_theta=0.5, tau_x=1.5)

# ModelMichael = TwiprModel(m_b=2.5, m_w=0.636, l=0.026, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648,
# I_x=0.02, I_z=0.03, c_alpha=4.6302e-4, r_w=0.055, tau_theta=0.75, tau_x=0.75)

# ModelMichael = TwiprModel(m_b=2.5, m_w=0.636, l=0.026, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648, I_x=0.02,
#                           I_z=0.03, c_alpha=4.6302e-4, r_w=0.055, tau_theta=0.75, tau_x=1.1)


ModelMichael = TwiprModel(m_b=2.5, m_w=0.636, l=0.026, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648, I_x=0.02,
                          I_z=0.03, c_alpha=4.6302e-4, r_w=0.055, tau_theta=0, tau_x=0)

ModelMichael_wrong = TwiprModel(m_b=3.8, m_w=0.636, l=0.035, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648, I_x=0.02,
                          I_z=0.03, c_alpha=4.6302e-4, r_w=0.07, tau_theta=0.1, tau_x=0.25)




class ModelMichael_additionalMass(TwiprModel):
    def __init__(self, ma):
        super().__init__(m_b=2.5 + ma, m_w=0.636, l=(0.026 * 2.5 + 0.2 * ma) / (ma + 2.5), d_w=0.28, I_w=5.1762e-4,
                         I_w2=6.1348e-04, I_y=0.01648 + 0.2 ** 2 * ma, I_x=0.02, I_z=0.03, c_alpha=4.6302e-4, r_w=0.055,
                         tau_theta=0, tau_x=0)


# TWIPR_2D_LINEAR ######################################################################################################
TWIPR_2D_StateSpace = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name='s'), core.spaces.Dimension(name='s_dot'),
                core.spaces.Dimension(name='theta', limits=[-pi, pi], wrapping=True),
                core.spaces.Dimension(name='theta_dot')])
TWIPR_2D_InputSpace = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name="M", unit="Nm")]
)


class TWIPR_2D_Linear(core.dynamics.LinearDynamics):
    model: TwiprModel
    K: np.ndarray

    def __init__(self, Ts, model: TwiprModel=ModelMichael, poles=None):
        self.model = model

        ss = TWIPR_2D_StateSpace

        A_cont, B_cont, C_cont, D_cont = self.linear_model()
        sys_cont = control.StateSpace(A_cont, B_cont, C_cont, D_cont, remove_useless_states=False)
        sys_disc = control.c2d(sys_cont, Ts)

        self.A = sys_disc.A
        self.B = sys_disc.B
        self.C = sys_disc.C
        self.D = sys_disc.D
        super().__init__("discrete", state_space=ss, Ts=Ts)

        if poles is not None:
            self.K = self.set_poles(poles)

    def set_poles(self, poles):
        poles = np.asarray(poles)
        K = np.asarray(control.place(self.A, self.B, np.exp(poles * self.Ts)))
        A_hat = self.A - self.B @ K
        self.A = A_hat
        self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)
        return K

    def linear_model(self):
        g = 9.81
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w

        A = [[0.000, 1, 0, 0],
             [0.000, -D_11 / V_1, -C_11 * g / V_1, D_12 / V_1],
             [0.000, 0, 0, 1],
             [0.000, D_21 / V_1, C_21 * g / V_1, -D_22 / V_1]]

        B_1 = (self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l
        B_2 = self.model.m_b * self.model.l / self.model.r_w + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2

        B = [[0],
             [B_1 / V_1],
             [0],
             [-B_2 / V_1]]

        C = [[0, 0, 1, 0]]

        D = 0

        return np.asarray(A), np.asarray(B), np.asarray(C), np.asarray(D)

# TWIPR_2D_NONLINEAR ###################################################################################################
class TWIPR_2D_Nonlinear(core.dynamics.Dynamics):
    model: TwiprModel
    K: np.ndarray  # Statefeedback
    linear_dynamics: core.dynamics.LinearDynamics


    # == INIT ==========================================================================================================
    def __init__(self, model: TwiprModel, Ts, poles=None, nominal_model = None):
        self.model = model

        if nominal_model is None:
            self.linear_dynamics = TWIPR_2D_Linear(model=model, Ts=Ts, poles=poles)
        else:
            self.linear_dynamics = TWIPR_2D_Linear(model=nominal_model, Ts=Ts, poles=poles)
        self.q = 1
        self.p = 1
        self.n = 4

        super().__init__(Ts=Ts, state_space=TWIPR_2D_StateSpace, input_space=TWIPR_2D_InputSpace)

        self.K = self.linear_dynamics.K



    # == PROPERTIES ====================================================================================================

    # == PRIVATE METHODS ===============================================================================================
    def _dynamics(self, state, input):
        g = 9.81

        s = state[0]
        v = state[1]
        theta = state[2]
        theta_dot = state[3]

        u = input - self.K @ state

        C_12 = (self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l
        C_22 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2 * np.cos(
            theta) ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - 2 * self.model.m_b * self.model.l * np.cos(
            theta) * self.model.c_alpha / self.model.r_w
        B_2 = self.model.m_b * self.model.l / self.model.r_w * np.cos(
            theta) + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
        B_1 = (
                      self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta)
        C_31 = 2 * (self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta)
        C_32 = self.model.m_b * self.model.l
        D_33 = self.model.d_w ** 2 / (2 * self.model.r_w ** 2) * self.model.c_alpha
        V_2 = self.model.I_z + 2 * self.model.I_w2 + (
                self.model.m_w + self.model.I_w / self.model.r_w ** 2) * self.model.d_w ** 2 / 2 - (
                      self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.sin(theta) ** 2
        B_3 = self.model.d_w / (2 * self.model.r_w)
        C_13 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l + self.model.m_b * self.model.l * (
                       self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta) ** 2
        C_23 = (self.model.m_b ** 2 * self.model.l ** 2 + (
                self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                        self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2)) * np.cos(theta)

        state_dot = np.zeros(self.n)

        state_dot[0] = v
        state_dot[1] = np.sin(theta) / V_1 * (-C_11 * g + C_12 * theta_dot ** 2) - D_11 / V_1 * v + D_12 / V_1 * theta_dot + B_1 / V_1*u[0] - self.model.tau_x * v
        state_dot[2] = theta_dot
        state_dot[3] = np.sin(theta) / V_1 * (
                C_21 * g - C_22 * theta ** 2) + D_21 / V_1 * v - D_22 / V_1 * theta_dot - B_2 / V_1 * (
                               u[0]) - self.model.tau_theta * theta_dot

        state = state + state_dot * self.Ts

        return state

    # ------------------------------------------------------------------------------------------------------------------
    def _output_function(self, state):
        output = state['theta']
        return output

    # == METHODS =======================================================================================================


# TWIPR_3D_LINEAR ######################################################################################################

TWIPR_3D_StateSpace_S = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name='s', unit='m'),
                core.spaces.Dimension(name='v', unit='m/s'),
                core.spaces.Dimension(name='theta', limits=[-pi, pi], wrapping=True, unit='rad'),
                core.spaces.Dimension(name='theta_dot', unit='rad/s'),
                core.spaces.Dimension(name='psi', limits=[0, 2 * pi], wrapping=True, unit='rad'),
                core.spaces.Dimension(name='psi_dot', unit='rad/s')])

TWIPR_3D_StateSpace = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name='x', unit='m'),
                core.spaces.Dimension(name='y', unit='m'),
                core.spaces.Dimension(name='v', unit='m/s'),
                core.spaces.Dimension(name='theta', limits=[-pi, pi], wrapping=True, unit='rad'),
                core.spaces.Dimension(name='theta_dot', unit='rad/s'),
                core.spaces.Dimension(name='psi', limits=[0, 2 * pi], wrapping=True, unit='rad'),
                core.spaces.Dimension(name='psi_dot', unit='rad/s')])

TWIPR_3D_InputSpace = core.spaces.StateSpace(
    dimensions=[core.spaces.Dimension(name="M_L", unit="Nm"),
                core.spaces.Dimension(name="M_R", unit="Nm")]
)


class TWIPR_3D_Linear(core.dynamics.LinearDynamics):
    model: TwiprModel
    K: np.ndarray

    # == INIT ==========================================================================================================
    def __init__(self, model: TwiprModel, Ts, poles=None, ev=None, xy=False):
        self.model = model

        if xy:
            ss = TWIPR_3D_StateSpace
        else:
            ss = TWIPR_3D_StateSpace_S

        A_cont, B_cont, C_cont, D_cont = self._linear_model(xy)
        self.sys_cont = control.StateSpace(A_cont, B_cont, C_cont, D_cont, remove_useless_states=False)
        sys_disc = control.c2d(self.sys_cont, Ts)

        self.A = sys_disc.A
        self.B = sys_disc.B
        self.C = sys_disc.C
        self.D = sys_disc.D

        super().__init__("discrete", state_space=ss, Ts=Ts)

        if poles is not None and ev is None:
            self.K = self.set_poles(poles)
        if poles is not None and ev is not None:
            self.K = self.set_eigenstructure(poles, ev)
        else:
            self.K = np.zeros((self.p, self.n))

    # == PROPERTIES ====================================================================================================

    # == PRIVATE METHODS ===============================================================================================

    def _linear_model(self, xy=False):
        g = 9.81
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - self.model.m_b * self.model.l * 2 * self.model.c_alpha / self.model.r_w
        D_33 = self.model.d_w / (2 * self.model.r_w ** 2) * self.model.c_alpha
        V_2 = self.model.I_z + 2 * self.model.I_w2 + (
                self.model.m_w + self.model.I_w / self.model.r_w ** 2) * self.model.d_w ** 2 / 2

        if xy:
            A = [[0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 1, 0],
                 [0, 0, -D_11 / V_1, -C_11 * g / V_1, D_12 / V_1, 0, 0],
                 [0, 0, 0, 0, 1, 0, 0],
                 [0, 0, D_21 / V_1, C_21 * g / V_1, -D_22 / V_1, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, -D_33 / V_2]]

            B_1 = (self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l
            B_2 = self.model.m_b * self.model.l / self.model.r_w + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
            B_3 = self.model.d_w / (2 * self.model.r_w)

            B = [[0, 0],
                 [0, 0],
                 [B_1 / V_1, B_1 / V_1],
                 [0, 0],
                 [-B_2 / V_1, -B_2 / V_1],
                 [0, 0],
                 [-B_3 / V_2, B_3 / V_2]]

            C = [[0, 0, 0, 1, 0, 0, 0]]

            D = [0, 0]

        else:
            A = [[0, 1, 0, 0, 0, 0],
                 [0, -D_11 / V_1, -C_11 * g / V_1, D_12 / V_1, 0, 0],
                 [0, 0, 0, 1, 0, 0],
                 [0, D_21 / V_1, C_21 * g / V_1, -D_22 / V_1, 0, 0],
                 [0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, -D_33 / V_2]]

            B_1 = (self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l
            B_2 = self.model.m_b * self.model.l / self.model.r_w + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
            B_3 = self.model.d_w / (2 * self.model.r_w)

            B = [[0, 0],
                 [B_1 / V_1, B_1 / V_1],
                 [0, 0],
                 [-B_2 / V_1, -B_2 / V_1],
                 [0, 0],
                 [-B_3 / V_2, B_3 / V_2]]

            C = [[0, 0, 1, 0, 0, 0]]

            D = [0, 0]

        return np.asarray(A), np.asarray(B), np.asarray(C), np.asarray(D)

    # == METHODS =======================================================================================================
    def set_poles(self, poles):
        poles = np.asarray(poles)

        if self.type == "discrete":
            self.K = np.asarray(control.place(self.A, self.B, np.exp(poles * self.Ts)))
        if self.type == 'cont':
            self.K = np.asarray(control.place(self.A, self.B, poles))

        A_hat = self.A - self.B @ self.K
        self.A = A_hat
        self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

        if self.type == 'discrete' and hasattr(self, 'sys_cont') and self.sys_cont is not None:
            K = np.asarray(control.place(self.sys_cont.A, self.sys_cont.B, poles))
            self.sys_cont = control.StateSpace((self.sys_cont.A - self.sys_cont.B @ K), self.sys_cont.B,
                                               self.sys_cont.C, self.sys_cont.D, remove_useless_states=False)

        return self.K

    # ------------------------------------------------------------------------------------------------------------------
    def set_eigenstructure(self, poles, ev, set=True):
        if len(poles) == 7:
            poles = poles[1:]
            ev = ev[1:, 1:]

        poles = np.asarray(poles)
        K = lib_control.eigenstructure_assignment(self.A, self.B, np.exp(poles * self.Ts), ev)
        if set:
            self.K = K
            A_hat = self.A - self.B @ self.K
            self.A = A_hat
            self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

        return K


# TWIPR_3D_NONLINEAR ###################################################################################################
class TWIPR_3D_Nonlinear(core.dynamics.Dynamics):
    model: TwiprModel
    K: np.ndarray  # Statefeedback
    linear_dynamics: core.dynamics.LinearDynamics

    # == INIT ==========================================================================================================
    def __init__(self, model: TwiprModel, Ts, poles=None, ev=None):
        self.model = model
        self.linear_dynamics = TWIPR_3D_Linear(self.model, Ts, poles, ev)
        self.q = 1
        self.p = 2
        self.n = 7

        if self.linear_dynamics.K.shape == (2, 6):
            self.K = np.hstack((np.zeros((self.p, 1)), self.linear_dynamics.K))
        elif self.linear_dynamics.K.shape == (2, 7):
            self.K = self.linear_dynamics.K

        super().__init__(Ts=Ts, state_space=TWIPR_3D_StateSpace, input_space=TWIPR_3D_InputSpace)

    # == PROPERTIES ====================================================================================================

    # == PRIVATE METHODS ===============================================================================================
    def _dynamics(self, state, input):
        g = 9.81

        x = state[0]
        y = state[1]
        v = state[2]
        theta = state[3]
        theta_dot = state[4]
        psi = state[5]
        psi_dot = state[6]

        u = input - self.K @ state

        C_12 = (self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l
        C_22 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        C_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * self.model.m_b * self.model.l
        V_1 = (self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                self.model.I_y + self.model.m_b * self.model.l ** 2) - self.model.m_b ** 2 * self.model.l ** 2 * np.cos(
            theta) ** 2
        D_22 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w
        D_21 = (
                       self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * 2 * self.model.c_alpha / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha / self.model.r_w ** 2
        C_11 = self.model.m_b ** 2 * self.model.l ** 2 * np.cos(theta)
        D_12 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w - self.model.m_b * self.model.l * np.cos(
            theta) * 2 * self.model.c_alpha
        D_11 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * 2 * self.model.c_alpha / self.model.r_w ** 2 - 2 * self.model.m_b * self.model.l * np.cos(
            theta) * self.model.c_alpha / self.model.r_w
        B_2 = self.model.m_b * self.model.l / self.model.r_w * np.cos(
            theta) + self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2
        B_1 = (
                      self.model.I_y + self.model.m_b * self.model.l ** 2) / self.model.r_w + self.model.m_b * self.model.l * np.cos(
            theta)
        C_31 = 2 * (self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta)
        C_32 = self.model.m_b * self.model.l
        D_33 = self.model.d_w ** 2 / (2 * self.model.r_w ** 2) * self.model.c_alpha
        V_2 = self.model.I_z + 2 * self.model.I_w2 + (
                self.model.m_w + self.model.I_w / self.model.r_w ** 2) * self.model.d_w ** 2 / 2 - (
                      self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.sin(theta) ** 2
        B_3 = self.model.d_w / (2 * self.model.r_w)
        C_13 = (
                       self.model.I_y + self.model.m_b * self.model.l ** 2) * self.model.m_b * self.model.l + self.model.m_b * self.model.l * (
                       self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2) * np.cos(theta) ** 2
        C_23 = (self.model.m_b ** 2 * self.model.l ** 2 + (
                self.model.m_b + 2 * self.model.m_w + 2 * self.model.I_w / self.model.r_w ** 2) * (
                        self.model.I_z - self.model.I_x - self.model.m_b * self.model.l ** 2)) * np.cos(theta)

        state_dot = np.zeros(self.n)

        state_dot[0] = v * np.cos(psi)
        state_dot[1] = v * np.sin(psi)
        state_dot[2] = np.sin(theta) / V_1 * (
                -C_11 * g + C_12 * theta_dot ** 2 + C_13 * psi_dot ** 2) - D_11 / V_1 * v + D_12 / V_1 * theta_dot + B_1 / V_1 * (
                               u[0] + u[1]) - self.model.tau_x * v
        state_dot[3] = theta_dot
        state_dot[4] = np.sin(theta) / V_1 * (
                C_21 * g - C_22 * theta ** 2 - C_23 * psi_dot ** 2) + D_21 / V_1 * v - D_22 / V_1 * theta_dot - B_2 / V_1 * (
                               u[0] + u[1]) - self.model.tau_theta * theta_dot
        state_dot[5] = psi_dot
        state_dot[6] = np.sin(theta) / V_2 * (
                C_31 * theta_dot * psi_dot - C_32 * psi_dot * v) - D_33 / V_2 * psi_dot - B_3 / V_2 * (
                               u[0] - u[1])

        state = state + state_dot * self.Ts

        return state

    # ------------------------------------------------------------------------------------------------------------------
    def _output_function(self, state):
        output = state['theta']
        return output

    # == METHODS =======================================================================================================
