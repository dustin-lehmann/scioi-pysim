import math

import numpy as np
from scioi_py_core import core as core
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

    def _init(self, *args, **kwargs):
        pass


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

    def __init__(self, height: float = 0.25, width: float = 0.16, depth: float = 0.08, wheel_diameter: float = 0.1,
                 l_w: float = 0.01, *args, **kwargs):
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
        self.bounding_objects['body'].orientation = config['ori']
        self._calcProximitySphere()

    def _calcProximitySphere(self):
        self.proximity_sphere.radius = self._getProximitySphereRadius()
        self.proximity_sphere.update(position=self.bounding_objects['body'].position)

    def _getProximitySphereRadius(self):
        return self.height / 2 * 1.1


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
        x = self.configuration_global
        x['pos'] = self.physics.bounding_objects['body'].position
        sample['configuration'] = x.serialize()
        return sample

    def _init(self, *args, **kwargs):
        self._updatePhysics()

