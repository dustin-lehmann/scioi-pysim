import copy
import dataclasses
import math
import time

import control
import numpy as np
from numpy import nan

from scioi_py_core import core as core
from scioi_py_core.core import spaces as sp
from scioi_py_core.utils import lib_control
from scioi_py_core.utils.orientations import twiprToRotMat, twiprFromRotMat

# === DEFINITIONS ======================================================================================================
Ts = 0.02


# === WORLD ============================================================================================================
class DynamicWorld_XYZR_Simple(core.world.World):
    space = core.spaces.Space3D()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Phases:
        # - Input
        # - Sensors
        # - Communication
        # - Logic
        # - Dynamics
        # - Environment
        # - Logic 2
        # - Output

        phase_input = core.scheduling.Action(name='input', object=self, function=self.action_input, priority=10)
        phase_sensors = core.scheduling.Action(name='sensors', object=self, function=self.action_sensors, priority=11)
        phase_communication = core.scheduling.Action(name='communication', object=self,
                                                     function=self.action_communication, priority=12)
        phase_logic = core.scheduling.Action(name='logic', object=self,
                                             function=self.action_logic, priority=13)
        phase_dynamics = core.scheduling.Action(name='dynamics', object=self,
                                                function=self.action_dynamics, priority=14)

        phase_physics_update = core.scheduling.Action(name='physics_update', object=self,
                                                      function=self.action_physics_update, priority=15)

        phase_collision = core.scheduling.Action(name='collision', object=self,
                                                 function=self.collisionCheck, priority=16)
        phase_logic2 = core.scheduling.Action(name='logic2', object=self,
                                              function=self.action_logic2, priority=17)
        phase_output = core.scheduling.Action(name='output', object=self,
                                              function=self.action_output, priority=18)

    # === Actions ======================================================================================================

    def action_input(self, *args, **kwargs):
        pass

    def action_sensors(self, *args, **kwargs):
        pass

    def action_communication(self, *args, **kwargs):
        pass

    def action_logic(self, *args, **kwargs):
        pass

    def action_dynamics(self, *args, **kwargs):
        pass

    def action_environment(self, *args, **kwargs):
        pass

    def action_logic2(self, *args, **kwargs):
        pass

    def action_output(self, *args, **kwargs):
        pass

    def action_physics_update(self, *args, **kwargs):
        pass

    def _init(self):
        super()._init()


# DYNAMICS =============================================================================================================
TankRobot_InputSpace = core.spaces.Space(dimensions=[
    core.spaces.ScalarDimension(name='v'),
    core.spaces.ScalarDimension(name='psi_dot'),
])

TankRobot_Spaces = core.dynamics.DynamicsSpaces()
TankRobot_Spaces.input_space = TankRobot_InputSpace
TankRobot_Spaces.state_space = core.spaces.Space2D()
TankRobot_Spaces.output_space = core.spaces.Space2D()


# Dynamics
class TankRobot_Dynamics(core.dynamics.Dynamics):
    spaces = TankRobot_Spaces
    Ts = Ts

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _dynamics(self, state: core.spaces.State, input: core.spaces.State, *args, **kwargs):
        state['pos']['x'] = state['pos']['x'] + self.Ts * input['v'] * np.cos(state['psi'].value)
        state['pos']['y'] = state['pos']['y'] + self.Ts * input['v'] * np.sin(state['psi'].value)
        state['psi'] = state['psi'] + self.Ts * input['psi_dot']

        return state

    def _output(self, state: core.spaces.State):
        output = self.spaces.output_space.getState()
        output['pos']['x'] = state['pos']['x']
        output['pos']['y'] = state['pos']['y']
        output['psi'] = state['psi']

    def _init(self, *args, **kwargs):
        pass


# PHYSICAL OBJECTS =====================================================================================================
class TankRobotPhysicalObject(core.physics.PhysicalBody):
    length: float
    width: float
    height: float

    def __init__(self, length: float = 0.157, width: float = 0.115, height: float = 0.052, *args, **kwargs):
        super().__init__()

        self.length = length
        self.width = width
        self.height = height

        self.bounding_objects = {
            'body': core.physics.CuboidPrimitive(size=[self.length, self.width, self.height], position=[0, 0, 0],
                                                 orientation=np.eye(3))
        }

        self.offset = [0, 0, self.height / 2]

        self.proximity_sphere.radius = self._getProximitySphereRadius()

    def update(self, position, orientation, *args, **kwargs):
        self.bounding_objects['body'].position = np.asarray(position) + np.asarray(self.offset)
        self.bounding_objects['body'].orientation = orientation
        self._calcProximitySphere()

    def _calcProximitySphere(self):
        self.proximity_sphere.radius = self._getProximitySphereRadius()
        self.proximity_sphere.update(position=self.bounding_objects['body'].position)

    def _getProximitySphereRadius(self):
        return (np.sqrt(self.length ** 2 + self.width ** 2 + self.height ** 2) / 2) * 1.1


# AGENTS ===============================================================================================================
class TankRobotSimObject(core.dynamics.DynamicWorldObject):
    object_type: str = 'tank_robot'
    space = core.spaces.Space2D()

    def __init__(self, *args, **kwargs):
        self.type = 'TankRobot'
        self.dynamics = TankRobot_Dynamics()
        self.physics: TankRobotPhysicalObject = TankRobotPhysicalObject(*args, **kwargs)
        super().__init__(*args, **kwargs, collision_check=True, collidable=True)

    def _updatePhysics(self, config=None, *args, **kwargs):
        self.physics.update(position=[self.configuration_global['pos']['x'], self.configuration['pos']['y'], 0],
                            orientation=self.configuration_global['rot'])

    def _getParameters(self):
        params = super()._getParameters()
        params['size'] = {
            'x': self.physics.length,
            'y': self.physics.width,
            'z': self.physics.height
        }
        return params

    def _init(self, *args, **kwargs):
        self._updatePhysics()


# TWIPR ================================================================================================================
class Space3D_TWIPR(core.spaces.Space):
    dimensions = [core.spaces.VectorDimension(name='pos', base_type=core.spaces.PositionVector2D),
                  core.spaces.ScalarDimension(name='theta', limits=[-math.pi, math.pi], wrapping=True),
                  core.spaces.ScalarDimension(name='psi', limits=[0, 2 * math.pi], wrapping=True)]

    def _add(self, state1, state2, new_state):
        raise Exception("Addition not allowed")


class Mapping_TWIPR_2_3D(core.spaces.SpaceMapping):
    space_to = core.spaces.Space3D
    space_from = Space3D_TWIPR

    def _map(self, state):
        out = {
            'pos': [state['pos']['x'], state['pos']['y'], 0],
            'ori': twiprToRotMat(state['theta'].value, state['psi'].value)
        }
        return out


class Mapping_3D_2_TWIPR(core.spaces.SpaceMapping):
    space_from = core.spaces.Space3D
    space_to = Space3D_TWIPR

    def _map(self, state):
        angles = twiprFromRotMat(state['ori'].value)
        out = {
            'pos': [state['pos']['x'], state['pos']['y']],
            'theta': angles[1],
            'psi': angles[0]
        }
        return out


Space3D_TWIPR.mappings = [Mapping_3D_2_TWIPR(), Mapping_TWIPR_2_3D()]
core.spaces.Space3D.mappings.append(Mapping_3D_2_TWIPR())


# ----------------------------------------------------------------------------------------------------------------------
class TWIPR_PhysicalObject(core.physics.PhysicalBody):
    height: float
    width: float
    depth: float

    def __init__(self, height: float = 0.174, width: float = 0.126, depth: float = 0.064, wheel_diameter: float = 0.13,
                 l_w: float = 0.056, *args, **kwargs):
        super().__init__()

        self.depth = depth
        self.width = width
        self.height = height
        self.wheel_diameter = wheel_diameter
        self.l_w = l_w

        self.bounding_objects = {
            'body': core.physics.CuboidPrimitive(size=[self.depth, self.width, self.height], position=[0, 0, 0],
                                                 orientation=np.eye(3))
        }

        self.proximity_sphere.radius = self._getProximitySphereRadius()

    def update(self, config, *args, **kwargs):
        v_t = [config['pos']['x'], config['pos']['y'], self.wheel_diameter / 2]
        v_m = [0, 0, self.height / 2 - self.l_w]
        v_m_e = config['ori'] * v_m
        new_position = v_t + v_m_e

        self.bounding_objects['body'].update(new_position, config['ori'].value)
        self._calcProximitySphere()

    def _calcProximitySphere(self):
        self.proximity_sphere.radius = self._getProximitySphereRadius()
        self.proximity_sphere.update(position=self.bounding_objects['body'].position)

    def _getProximitySphereRadius(self):
        return self.height / 2 * 1.1


# ----------------------------------------------------------------------------------------------------------------------


class TWIPR_3D_InputSpace(core.spaces.Space):
    dimensions = [core.spaces.ScalarDimension(name='M_L'),
                  core.spaces.ScalarDimension(name='M_R')]


class TWIPR_3D_ExternalInputSpace(core.spaces.Space):
    dimensions = [core.spaces.ScalarDimension(name='v'),
                  core.spaces.ScalarDimension(name='psi_dot')]


class TWIPR_3D_StateSpace_6D(core.spaces.Space):
    dimensions = [core.spaces.ScalarDimension(name='s'),
                  core.spaces.ScalarDimension(name='v'),
                  core.spaces.ScalarDimension(name='theta'),
                  core.spaces.ScalarDimension(name='theta_dot'),
                  core.spaces.ScalarDimension(name='psi'),
                  core.spaces.ScalarDimension(name='psi_dot')]


class TWIPR_3D_StateSpace_7D(core.spaces.Space):
    dimensions = [core.spaces.ScalarDimension(name='x'),
                  core.spaces.ScalarDimension(name='y'),
                  core.spaces.ScalarDimension(name='v'),
                  core.spaces.ScalarDimension(name='theta', wrapping=False),
                  core.spaces.ScalarDimension(name='theta_dot'),
                  core.spaces.ScalarDimension(name='psi'),
                  core.spaces.ScalarDimension(name='psi_dot')]


class Mapping_TWIPR_SS_2_TWIPR_CF(core.spaces.SpaceMapping):
    space_from = TWIPR_3D_StateSpace_7D
    space_to = Space3D_TWIPR

    def _map(self, state):
        out = {
            'pos': [state['x'], state['y']],
            'theta': state['theta'],
            'psi': state['psi']
        }
        return out


class Mapping_TWIPR_CF_2_TWIPR_SS(core.spaces.SpaceMapping):
    space_from = Space3D_TWIPR
    space_to = TWIPR_3D_StateSpace_7D

    def _map(self, state):
        out = {
            'x': state['pos']['x'],
            'y': state['pos']['y'],
            'theta': state['theta'],
            'psi': state['psi']
        }
        return out


TWIPR_3D_StateSpace_7D.mappings = [Mapping_TWIPR_SS_2_TWIPR_CF(), Mapping_TWIPR_CF_2_TWIPR_SS()]


@dataclasses.dataclass
class TwiprModel:
    m_b: float
    m_w: float
    l: float
    d_w: float
    I_w: float
    I_w2: float
    I_y: float
    I_x: float
    I_z: float
    c_alpha: float
    r_w: float
    tau_theta: float
    tau_x: float
    max_pitch: float


TWIPR_Michael_Model = TwiprModel(m_b=2.5, m_w=0.636, l=0.026, d_w=0.28, I_w=5.1762e-4, I_w2=6.1348e-04, I_y=0.01648,
                                 I_x=0.02,
                                 I_z=0.03, c_alpha=4.6302e-4, r_w=0.055, tau_theta=1, tau_x=1,
                                 max_pitch=np.deg2rad(105))


class TWIPR_3D_Linear(core.dynamics.LinearDynamics):
    model: TwiprModel
    K: np.ndarray
    input_space = TWIPR_3D_InputSpace()
    output_space = TWIPR_3D_StateSpace_6D()
    state_space = TWIPR_3D_StateSpace_6D()

    # == INIT ==========================================================================================================
    def __init__(self, model: TwiprModel, Ts, poles=None, ev=None):
        self.model = model
        self.Ts = Ts

        A_cont, B_cont, C_cont, D_cont = self._linear_model()
        self.sys_cont = control.StateSpace(A_cont, B_cont, C_cont, D_cont, remove_useless_states=False)
        sys_disc = control.c2d(self.sys_cont, Ts)

        self.A = sys_disc.A
        self.B = sys_disc.B
        self.C = sys_disc.C
        self.D = sys_disc.D

        super().__init__(Ts=Ts)

        if poles is not None and ev is None:
            self.K = self.set_poles(poles)
        if poles is not None and ev is not None:
            self.K = self.set_eigenstructure(poles, ev)
        else:
            self.K = np.zeros((self.p, self.n))

    def _linear_model(self):

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

        self.K = np.asarray(control.place(self.A, self.B, np.exp(poles * self.Ts)))

        A_hat = self.A - self.B @ self.K
        self.A = A_hat
        self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

        if hasattr(self, 'sys_cont') and self.sys_cont is not None:
            K = np.asarray(control.place(self.sys_cont.A, self.sys_cont.B, poles))
            self.sys_cont = control.StateSpace((self.sys_cont.A - self.sys_cont.B @ K), self.sys_cont.B,
                                               self.sys_cont.C, self.sys_cont.D, remove_useless_states=False)

        return self.K

    # ------------------------------------------------------------------------------------------------------------------
    def set_eigenstructure(self, poles, ev, set=True):

        poles = np.asarray(poles)
        K = lib_control.eigenstructure_assignment(self.A, self.B, np.exp(poles * self.Ts), ev)
        if set:
            self.K = K
            A_hat = self.A - self.B @ self.K
            self.A = A_hat
            self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

        return K


class TWIPR_Dynamics_3D(core.dynamics.Dynamics):

    def _init(self):
        pass

    state_space = TWIPR_3D_StateSpace_7D()
    input_space = TWIPR_3D_InputSpace()
    output_space = TWIPR_3D_StateSpace_7D()
    model: TwiprModel

    # == INIT ==========================================================================================================
    def __init__(self, model: TwiprModel, Ts, poles=None, eigenvectors=None, speed_control: bool = False, *args,
                 **kwargs):
        super().__init__(Ts=Ts, *args, **kwargs)
        self.model = model

        self.state_space['theta'].limits = [-self.model.max_pitch, self.model.max_pitch]

        self.q = 1
        self.p = 2
        self.n = 7

    # == METHODS ====================================================================================================
    def update(self, input=None):
        if input is not None:
            self.input = input
        self.state = self._dynamics(self.state, self.input)

    # == PRIVATE METHODS ===============================================================================================
    def _dynamics(self, state, input):
        g = 9.81

        x = state[0].value
        y = state[1].value
        v = state[2].value
        theta = state[3].value
        theta_dot = state[4].value
        psi = state[5].value
        psi_dot = state[6].value

        u = [input[0].value, input[1].value]

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

    # ------------------------------------------------------------------------------------------------------------------
    def _output(self, state):
        output = state['theta']
        return output

    # == METHODS =======================================================================================================


twipr_3d_poles_default = [0, -20, -3 + 1j, -3 - 1j, 0, -1.5]
twipr_3d_ev_default = np.array([[1, nan, nan, nan, 0, nan],
                                [nan, 1, nan, nan, nan, nan],
                                [nan, nan, 1, 1, nan, 0],
                                [nan, nan, nan, nan, nan, nan],
                                [0, nan, nan, nan, 1, 1],
                                [nan, 0, 0, 0, nan, nan]])


# ----------------------------------------------------------------------------------------------------------------------
class TWIPR_Agent(core.agents.Agent):
    object_type = 'twipr_agent'
    space = Space3D_TWIPR()

    def __init__(self, world, agent_id, *args, **kwargs):
        super().__init__(world=world, agent_id=agent_id, *args, **kwargs)

        self.physics: TWIPR_PhysicalObject = TWIPR_PhysicalObject()

    def _getParameters(self):
        params = super()._getParameters()
        params['physics'] = {}

        params['size'] = {
            'x': self.physics.depth,
            'y': self.physics.width,
            'z': self.physics.height
        }
        params['physics']['size'] = [self.physics.depth, self.physics.width, self.physics.height]
        params['physics']['wheel_diameter'] = self.physics.wheel_diameter
        params['physics']['l_w'] = self.physics.l_w
        return params

    def _getSample(self):
        sample = super()._getSample()
        sample['collision_box_pos'] = {'x': self.physics.bounding_objects['body'].position[0],
                                       'y': self.physics.bounding_objects['body'].position[1],
                                       'z': self.physics.bounding_objects['body'].position[2]}

        return sample

    def _init(self, *args, **kwargs):
        self._updatePhysics()


# ----------------------------------------------------------------------------------------------------------------------
class TWIPR_DynamicAgent(TWIPR_Agent, core.agents.DynamicAgent):
    object_type = 'twipr_agent'
    space = Space3D_TWIPR()
    dynamics_class = TWIPR_Dynamics_3D

    input_space: TWIPR_3D_ExternalInputSpace()
    input: core.spaces.State
    poles: list
    eigenvectors: list
    K: np.ndarray
    controller_v: lib_control.PID_ctrl
    controller_psidot: lib_control.PID_ctrl

    linear_dynamics: TWIPR_3D_Linear

    Ts = 0.02

    def __init__(self, world, agent_id, speed_control: bool = False, poles=None, eigenvectors=twipr_3d_ev_default,
                 *args, **kwargs):
        if poles is None:
            poles = twipr_3d_poles_default

        self.dynamics = self.dynamics_class(Ts=0.02, model=TWIPR_Michael_Model)  # TODO: THIS IS REALLY BAD!

        super().__init__(world=world, agent_id=agent_id, *args, **kwargs)

        self.physics: TWIPR_PhysicalObject = TWIPR_PhysicalObject()

        if speed_control:
            self.controller_v = lib_control.PID_ctrl(Ts=self.Ts, P=-1.534 / 2, I=-2.81 / 2, D=-0.07264 / 2, max_rate=75)
            self.controller_psidot = lib_control.PID_ctrl(Ts=self.Ts, P=-0.3516, I=-1.288, D=-0.0002751)
            self.input_space = TWIPR_3D_ExternalInputSpace()
        else:
            self.controller_v = None
            self.controller_psidot = None
            self.input_space = TWIPR_3D_InputSpace()

        self.linear_dynamics = TWIPR_3D_Linear(self.dynamics.model, Ts, poles, eigenvectors)
        self.K = np.hstack((np.zeros((2, 1)), self.linear_dynamics.K))
        self.input = self.input_space.getState()

        core.scheduling.Action(name='logic', function=self._controller, object=self)

    # ------------------------------------------------------------------------------------------------------------------
    def _controller(self, input=None):

        if input is not None:
            self.input = input

        if self.controller_v is not None and self.controller_psidot is not None:
            e_v = self.input['v'] - self.dynamics.state['v']
            u_v = self.controller_v.update(e_v.value)

            e_psidot = self.input['psi_dot'] - self.dynamics.state['psi_dot']
            u_psidot = self.controller_psidot.update(e_psidot.value)

            input_dynamics = self.dynamics.input_space.map([u_v + u_psidot, u_v - u_psidot])
        else:
            input_dynamics = self.input

        input_dynamics = input_dynamics - self.K @ self.state

        self.dynamics.input = input_dynamics

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value: (list, np.ndarray, core.spaces.State)):
        self._input = self.input_space.map(value)

    # ------------------------------------------------------------------------------------------------------------------
    def _getParameters(self):
        params = super()._getParameters()
        params['physics'] = {}

        params['size'] = {
            'x': self.physics.depth,
            'y': self.physics.width,
            'z': self.physics.height
        }
        params['physics']['size'] = [self.physics.depth, self.physics.width, self.physics.height]
        params['physics']['wheel_diameter'] = self.physics.wheel_diameter
        params['physics']['l_w'] = self.physics.l_w
        return params

    def _getSample(self):
        sample = super()._getSample()
        return sample

    def _init(self, *args, **kwargs):
        self._updatePhysics()

    def _action_control(self):
        ...


standard_reference_trajectory = y_ref = [0 ,0.000197760222250443, 2.11803678398722e-05, -0.00192431976122926, -0.00615332730270171, -0.0109469705842174, -0.0109726750284568, 0.00314109970339850, 0.0424997242039622, 0.112410684401934, 0.206956128623623, 0.314388776117438, 0.424624384030855, 0.531504092587520, 0.632344339907318, 0.726580774482237, 0.814500854214386, 0.896435127229825, 0.972408345000750, 1.04209766198346, 1.10493026693230, 1.16020644070794, 1.20720625476184, 1.24529862610457, 1.27410193519773, 1.29373142884650, 1.30509563459453, 1.31006134120138, 1.31110201565285, 1.31047295027832, 1.30963323863495, 1.30922177157536, 1.30930631662257, 1.30965982770113, 1.30996481191886, 1.30994972434867, 1.30949786773374, 1.30875254893503, 1.30818871082097, 1.30855196124135, 1.31051378028126, 1.31390920626002, 1.31658347179794, 1.31325479714354, 1.29544137534898, 1.25367888373710, 1.18092399658192, 1.07430141167592, 0.934822844842898,	0.766570547670360,	0.576190859740028,	0.372759963677128,	0.167424548076854,	-0.0283162793280289,	-0.207136794339771,	-0.368318377418767,	-0.513567846522248,	-0.642925092434494,	-0.754407918301252,	-0.844997331803202,	-0.912193494933843,	-0.955634172298121,	-0.978235135241612,	-0.985958478482436,	-0.985709523100663,	-0.982841873248806,	-0.980233404456636,	-0.978812523403062,	-0.978465073275781,	-0.978773146960503,	-0.979413455756401	-0.980247798771826,	-0.981219159659383,	-0.982180374666072,	-0.982769568783324,	-0.982426074885620,	-0.980609358807766,	-0.977224675287443,	-0.973154087874496,	-0.970636351537536,	-0.973065802731135,	-0.983677050076961,	-1.00270542555312,	-1.02317436868087,	-1.02666525392914,	-0.982336312751358,	-0.854772438038150,	-0.627994145762945,	-0.352177508147913,	-0.125419966807256,	0.00210811409895107, 0.0463974593171859,	0.0428788688598347,	0.0224111802076914,	0.00342562788370501	-0.00710124071239199,	-0.00942546473025664,	-0.00682637673985390,	-0.00275955516620977,	0.000481842027831330,	0.00200718542849226, 0.00199239375341818,	0.00117230609516377, 0.000378721640301647, 0.000183951257060003, 0.00062972961798011, 0.00103310868987361, -4.31887979877787e-05]

# ======================================================================================================================
class TWIPR_ILC_Agent(TWIPR_DynamicAgent):
    reference: np.ndarray  # Reference trajectory
    K: int  # Length of reference trajectory
    j: int  # Current trial
    k: int  # Current sample index in trial
    u_j: np.ndarray  # Current input
    y_j: np.ndarray  # Current output
    e_j: np.ndarray  # Current error
    trials: list  # To save previous trials
    J_max: int = 30  # Maximum number of trials
    initial_state: core.spaces.State  # Initial State

    collision_during_trial: bool

    L: np.ndarray  # Learning Matrix
    Q: np.ndarray  # Q Filter

    wait_steps: int
    trial_state: str  # Can be 'trial', 'wait_before_trial' or 'wait_after_trial'

    learning_finished_flag: bool
    learning_successful: bool

    def __init__(self, world, agent_id, reference: np.ndarray, wait_steps: int = 50, r: float = 0.1, s: float = 0.5,
                 initial_state: list = None,
                 *args, **kwargs):
        super().__init__(world=world, agent_id=agent_id)

        self.reference = reference
        self.K = len(self.reference)
        self.j = 0
        self.k = 0
        self.u_j = np.zeros(shape=self.reference.shape)
        self.y_j = np.zeros(shape=self.reference.shape)
        self.wait_steps = wait_steps
        self.collision_during_trial = False
        self.trials = []

        if initial_state is None:
            initial_state = [-1, 0, 0, 0, 0, 0, 0]

        self.initial_state = self.dynamics.state_space.map(initial_state)
        self.trial_state = 'wait_before_trial'
        self.learning_finished_flag = False
        self.learning_successful = False

        self.setILC(r, s)

        core.scheduling.Action(name='input', object=self, function=self._action_input)
        core.scheduling.Action(name='logic2', object=self, function=self.update_after_step)

    # ------------------------------------------------------------------------------------------------------------------
    def setILC(self, r, s):

        P = lib_control.calc_transition_matrix(self.linear_dynamics.sys, self.K)

        Qw = np.eye(self.K)
        Rw = r * np.eye(self.K)
        Sw = s * np.eye(self.K)
        self.Q, self.L = lib_control.qlearning(P, Qw, Rw, Sw)

    # ------------------------------------------------------------------------------------------------------------------
    def update_after_step(self):
        if self.k == self.K - 1:
            self.update_after_trial()
        else:
            self.y_j[self.k] = self.state['theta']

            self.collision_during_trial = self.collision_during_trial or self.collision.collision_state
            self.k = self.k + 1

    # ------------------------------------------------------------------------------------------------------------------
    def update_after_trial(self):

        # Calculate the error signal
        self.e_j = self.reference - self.y_j

        # Save the current data
        self.trials.append({
            'u': copy.copy(self.u_j),
            'y': copy.copy(self.y_j),
            'e': copy.copy(self.e_j),
            'e_norm': np.linalg.norm(self.e_j),
            'collision': self.collision_during_trial
        })

        # Check if we had a collision during the trial
        if not self.collision_during_trial:
            # SUCCESS
            self.learning_finished_flag = True
            self.learning_successful = True

        if self.j == self.J_max - 1:
            # FAILURE
            self.learning_finished_flag = True
            self.learning_successful = False

        # Calculate the new input
        self.u_j = self.Q @ (self.u_j + self.L @ self.e_j)
        self.j = self.j + 1
        # Set the state to wait after trial
        self.trial_state = 'wait_after_trial'
        self.collision_during_trial = False
        self.k = 0

    # ------------------------------------------------------------------------------------------------------------------
    def _action_input(self):
        if not self.learning_finished_flag:
            if self.trial_state == 'trial':
                self.input = [self.u_j[self.k] / 2, self.u_j[self.k] / 2]
            elif self.trial_state == 'wait_after_trial' or self.trial_state == 'wait_before_trial':
                self.input = [0, 0]
        else:
            self.input = [0, 0]

    def _action_entry(self, *args, **kwargs):
        super()._action_entry(*args, **kwargs)

        if self.trial_state == 'wait_before_trial' and self.k == self.wait_steps:
            self.k = 0
            self.trial_state = 'trial'
        elif self.trial_state == 'wait_after_trial' and self.k == self.wait_steps:
            self.k = 0
            self.trial_state = 'wait_before_trial'
            self.state = copy.copy(self.initial_state)  # COULD BE DANGEROUS

    def _action_exit(self, *args, **kwargs):
        super()._action_exit(*args, **kwargs)
