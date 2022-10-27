from scioi_py_core import core as core

from EnvironmentDustin.Environment.objects import EnvironmentTWIPR_objects
import scioi_py_core.utils.joystick.joystick as joystick
# from EnvironmentDustin.baseline.baseline_environment import BabylonVisualization


class EnvironmentTWIPR(core.environment.Environment):
    # babylon: BabylonVisualization
    world: EnvironmentTWIPR_objects.DynamicWorld_XYZR_Simple
    joystick: joystick.Joystick
    run_mode = 'rt'
    Ts = 0.02
    name = 'environment'

    def __init__(self, visualization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = EnvironmentTWIPR_objects.DynamicWorld_XYZR_Simple(name='world', parent=self)
        self.visualization = visualization

        # if self.visualization == 'babylon':
        #     self.babylon = BabylonVisualization(*args, **kwargs)
        # else:
        #     self.babylon = None

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
