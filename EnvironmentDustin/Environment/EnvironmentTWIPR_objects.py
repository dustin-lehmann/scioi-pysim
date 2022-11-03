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

        self.bounding_objects['body'].position = new_position
        self.bounding_objects['body'].orientation = config['ori'].value
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


TWIPR_3D_StateSpace_7D.mappings = [Mapping_TWIPR_SS_2_TWIPR_CF()]


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

    def __init__(self, world, agent_id, speed_control: bool = False, poles=None, eigenvectors=twipr_3d_ev_default, *args, **kwargs):
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
    def _controller(self, input = None):

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
    def input(self, value):
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
