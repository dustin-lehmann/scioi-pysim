import random

from scioi_py_core import core as core

from EnvironmentDustin.Environment import EnvironmentTWIPR_objects
from scioi_py_core.visualization.babylon.babylon import BabylonVisualization
import scioi_py_core.utils.joystick.joystick as joystick
from scioi_py_core.utils.babylon import babylon_status_string, setBabylonStatus, getBabylonStatus


class EnvironmentBase(core.environment.Environment):
    babylon: (BabylonVisualization, None)
    world: EnvironmentTWIPR_objects.DynamicWorld_XYZR_Simple
    joystick: joystick.Joystick
    run_mode = 'rt'
    Ts = 0.02
    name = 'environment'

    def __init__(self, visualization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = EnvironmentTWIPR_objects.DynamicWorld_XYZR_Simple(name='world', parent=self)
        self.visualization = visualization

        if self.visualization == 'babylon':
            self.babylon = BabylonVisualization(*args, **kwargs)
        else:
            self.babylon = None

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

        # self.joystick = joystick.Joystick()

    # === ACTIONS ======================================================================================================
    def _init(self, *args, **kwargs):
        ...
        # Set the world configuration in the babylon visualization if needed
        if self.visualization == 'babylon':
            self.babylon.setWorldConfig(self.world.generateWorldConfig())
            self.babylon.start()

    def _action_entry(self, *args, **kwargs):
        super()._action_entry(*args, **kwargs)
        setBabylonStatus('')

    def _action_step(self, *args, **kwargs):
        pass

    def action_input(self, *args, **kwargs):
        pass

    def action_controller(self, *args, **kwargs):
        pass

    def action_visualization(self, *args, **kwargs):
        sample = {
            'time': self.scheduling.tick_global * self.Ts,
            'status': getBabylonStatus(),
            'world': self.world.getSample()
        }
        self.babylon.sendSample(sample)

    def action_output(self, *args, **kwargs):
        pass

    def action_world(self, *args, **kwargs):
        pass
