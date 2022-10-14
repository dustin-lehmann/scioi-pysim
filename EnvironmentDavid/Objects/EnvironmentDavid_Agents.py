import numpy as np

import scioi_py_core.core as core
import scioi_py_core.utils.orientations as ori
from scioi_py_core.core.obstacles import FloorTile

from . import EnvironmentDavid_Dynamics
from . import EnvironmentDavid_World

# === TankRobot ========================================================================================================
TankRobotSpaces = core.dynamics.DynamicWorldObjectSpaces()
TankRobotSpaces.state_space = EnvironmentDavid_Dynamics.TankRobot_StateSpace
TankRobotSpaces.input_space = EnvironmentDavid_Dynamics.TankRobot_InputSpace
TankRobotSpaces.output_space = EnvironmentDavid_Dynamics.TankRobot_StateSpace
TankRobotSpaces.config_space = EnvironmentDavid_World.configuration_space_world
TankRobotSpaces.map_statespace_to_configspace = core.spaces.Mapping(
    space_from=TankRobotSpaces.state_space,
    space_to=EnvironmentDavid_World.configuration_space_world,
    mapping=lambda state:
    [
        state['x'],
        state['y'],
        0,
        ori.rotmatFromPsi(state['psi'])
    ]
)


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
            'body': core.physics.CuboidPrimitive(dimensions=[self.length, self.width, self.height], position=[0, 0, 0],
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


class TankRobotSimObject(core.dynamics.DynamicWorldObject):
    spaces = TankRobotSpaces

    def __init__(self, *args, **kwargs):
        self.type = 'TankRobot'
        self.dynamics = EnvironmentDavid_Dynamics.TankRobot_Dynamics()
        self.physics: TankRobotPhysicalObject = TankRobotPhysicalObject(*args, **kwargs)
        super().__init__(*args, **kwargs, collision_check=True, collidable=True, collision_excludes=[FloorTile])

    def action_physics_update(self, config, *args, **kwargs):
        self.physics.update(position=[self.configuration['x'], self.configuration['y'], 0],
                            orientation=self.configuration['rot'])

    @property
    def sample_params(self):  # todo
        params = {'length': self.physics.bounding_objects['body'].dimensions[0],
                  'width': self.physics.bounding_objects['body'].dimensions[1],
                  'height': self.physics.bounding_objects['body'].dimensions[2]}
        return params

    def _init(self, *args, **kwargs):
        self.dynamics.state = [0, 0, 0]
        self.action_physics_update(self.configuration)
