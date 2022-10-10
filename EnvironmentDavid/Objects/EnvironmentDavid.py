import scioi_py_core.utils.joystick.joystick
from scioi_py_core import core as core
from . import EnvironmentDavid_World
import scioi_py_core.utils.joystick.joystick as joystick
from EnvironmentDavid.baseline.baseline_environment import BabylonVisualization


class EnvironmentDavid(core.environment.Environment):
    babylon_env: BabylonVisualization
    world: EnvironmentDavid_World.DynamicWorld_XYZR_Simple
    joystick: joystick.Joystick
    run_mode = 'rt'
    Ts = 0.02

    # parameters that determine the size and amount of tiles the testbed has
    size_x: float = 5.094  # todo: put those values somewhere it makes sense
    size_y: float = 3.679
    tiles_x: int = 18
    tiles_y: int = 13

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = EnvironmentDavid_World.DynamicWorld_XYZR_Simple(name='World', parent=self)
        # babylon environment for visualization
        self.babylon_env = BabylonVisualization(*args, *kwargs)
        self.name = 'Environment'

        # Actions
        core.scheduling.Action(name='input', object=self, priority=0, parent=self.action_step,
                               function=self.action_input)
        core.scheduling.Action(name='controller', object=self, priority=1, parent=self.action_step,
                               function=self.action_controller)
        core.scheduling.Action(name='world', object=self, function=self.action_world, priority=2,
                               parent=self.action_step)

        core.scheduling.Action(name='visualization', object=self, priority=3, parent=self.action_step,
                               function=self.action_visualization)
        core.scheduling.Action(name='output', object=self, priority=4, parent=self.action_step,
                               function=self.action_output)

        core.scheduling.registerActions(self.world, self.scheduling.actions['world'])
        self.joystick = joystick.Joystick()

    # todo remove from here
    @property
    def tile_size(self) -> dict:
        """
        calculate tilesize from the size of the testbed and the number of tiles for x and y
        :return: list with tilesize [x,y]
        """
        x_limits = self.world.spaces.coordinate_space.dimensions[0].limits
        x_size = x_limits[1] - x_limits[0]
        y_limits = self.world.spaces.coordinate_space.dimensions[1].limits
        y_size = y_limits[1] - y_limits[0]
        tilesize = {'x': x_size / self.tiles_x,
                    'y': y_size / self.tiles_y}

        return tilesize

    # === ACTIONS ======================================================================================================

    def _action_step(self, *args, **kwargs):
        pass

    def _init(self, *args, **kwargs):
        pass

    def action_input(self, *args, **kwargs):
        pass

    def action_controller(self, *args, **kwargs):
        pass

    def action_visualization(self, *args, **kwargs):
        pass

    def action_output(self, *args, **kwargs):
        pass

    def action_world(self, *args, **kwargs):
        pass
