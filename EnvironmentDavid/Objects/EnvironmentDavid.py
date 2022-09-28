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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = EnvironmentDavid_World.DynamicWorld_XYZR_Simple(name='World', parent=self)
        # babylon environment for visualization
        self.babylon_env = BabylonVisualization()
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
