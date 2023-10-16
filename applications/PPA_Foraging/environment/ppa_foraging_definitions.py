import numpy as np

from scioi_py_core import core as core
from scioi_py_core.core import spaces as sp
from scioi_py_core.utils import lib_control
from scioi_py_core.utils.orientations import twiprToRotMat, twiprFromRotMat
from scioi_py_core.utils.babylon import setBabylonSettings


# === CONSTANTS ===
SAMPLE_TIME = 0.01

# === SPACES ===
robot_input_space = core.spaces.Space(dimensions=[
    core.spaces.ScalarDimension(name='v'),
    core.spaces.ScalarDimension(name='r'),
])
robot_state_space = core.spaces.Space2D()
robot_output_space = core.spaces.Space2D()


robot_spaces = core.dynamics.DynamicsSpaces()
robot_spaces.input_space = robot_input_space
robot_spaces.state_space = robot_state_space
robot_spaces.output_space = robot_output_space


# === Dynamics ===
class RobotDynamics(core.dynamics.Dynamics):
    input_space = robot_input_space
    state_space = robot_state_space
    output_space = robot_output_space
    Ts = SAMPLE_TIME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _dynamics(self, state: core.spaces.State, input: core.spaces.State, *args, **kwargs):
        state['pos']['x'] = state['pos']['x'] + self.Ts * input['v'] * np.cos(state['psi'].value)
        state['pos']['y'] = state['pos']['y'] + self.Ts * input['v'] * np.sin(state['psi'].value)
        state['psi'] = state['psi'] + self.Ts * input['r']

        return state

    def _output(self, state: core.spaces.State):
        output = self.spaces.output_space.getState()
        output['pos']['x'] = state['pos']['x']
        output['pos']['y'] = state['pos']['y']
        output['psi'] = state['psi']

    def _init(self, *args, **kwargs):
        pass

# === Physics ===
class RobotPhysics(core.physics.PhysicalBody):
    length: float
    width: float
    height: float

    def __init__(self, length: float = 0.15, width: float = 0.115, height: float = 0.05, *args, **kwargs):
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

# === Robot ===
class Robot_Base(core.agents.DynamicAgent):
    object_type: str = 'diff_drive_robot'
    space = core.spaces.Space2D()

    def __init__(self, *args, **kwargs):
        # self.type = 'DiffDriveRobot'
        self.dynamics = RobotDynamics()
        self.physics: RobotPhysics = RobotPhysics(*args, **kwargs)
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


# === OBJECTS ===

class GoalArea(core.world.WorldObject):
    ...

class Obstacle(core.obstacles.Obstacle):
    ...

class CollectableObject(core.world.WorldObject):
    ...

# === WORLD ===
class Dynamic2DWorld_Base(core.world.World):
    space = core.spaces.Space3D()
    obstacles: list[Obstacle] = []
    collectable_objects: list[CollectableObject] = []
    goal_area: GoalArea = None

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


