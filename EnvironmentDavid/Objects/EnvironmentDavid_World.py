import numpy as np

from scioi_py_core import core as core

# Definitions
world_x_min = 0.0
world_x_max = 5.094

world_y_min = 0.0
world_y_max = 3.679

world_z_min = -100.0
world_z_max = 100.0

# === SPACES ===========================================================================================================
coordinate_space_world = core.spaces.Space(dimensions=[
    core.spaces.Dimension(name='x', limits=[world_x_min, world_x_max],
                          wrapping=True),
    core.spaces.Dimension(name='y', limits=[world_y_min, world_y_max],
                          wrapping=True),
    core.spaces.Dimension(name='z',
                          wrapping=False),
]
)

configuration_space_world = core.spaces.Space(dimensions=[
    core.spaces.Dimension(name='x', limits=[world_x_min, world_x_max],
                          wrapping=True),
    core.spaces.Dimension(name='y', limits=[world_y_min, world_y_max],
                          wrapping=True),
    core.spaces.Dimension(name='z',
                          wrapping=True),
    core.spaces.Dimension(name='rot', dimension=(3, 3), type=np.ndarray)  # Rotation Matrix
])

space_map_cfs_to_cos = core.spaces.Mapping(space_from=configuration_space_world, space_to=coordinate_space_world,
                                           mapping=lambda config: [config['x'], config['y'], config['z']])

world_spaces_XYZR = core.world.WorldSpaces()
world_spaces_XYZR.coordinate_space = coordinate_space_world
world_spaces_XYZR.configuration_space = configuration_space_world
world_spaces_XYZR.map_configToCoordinateSpace = space_map_cfs_to_cos


# === WORLD ============================================================================================================
class DynamicWorld_XYZR_Simple(core.world.World):
    spaces = world_spaces_XYZR

    tiles_x: int = 18
    tiles_y: int = 13

    def __init__(self, *args, **kwargs):
        super().__init__(self.spaces, *args, **kwargs)

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

    # ===Testbed_properties=============================================================================================
    @property
    def tile_size(self) -> dict:
        """
        calculate tilesize from the size of the testbed and the number of tiles for x and y
        :return: list with tilesize [x,y]
        """
        x_limits = self.spaces.coordinate_space.dimensions[0].limits
        x_size = x_limits[1] - x_limits[0]
        y_limits = self.spaces.coordinate_space.dimensions[1].limits
        y_size = y_limits[1] - y_limits[0]
        tilesize = {'x': x_size / self.tiles_x,
                    'y': y_size / self.tiles_y}

        return tilesize

    # ===Actions========================================================================================================

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
