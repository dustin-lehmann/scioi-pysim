from scioi_py_core import core as core
from applications.PPA_Foraging.environment.ppa_foraging_definitions import Dynamic2DWorld_Base, Robot_Base, SAMPLE_TIME
from scioi_py_core.visualization.babylon.babylon import BabylonVisualization
from scioi_py_core.utils.babylon import getBabylonSettings, setBabylonSettings
from scioi_py_core.visualization.simple_2d.simple_2d_visualization import Simple2DVisualization


class EnvironmentBase(core.environment.Environment):
    babylon: (BabylonVisualization, None)
    world: Dynamic2DWorld_Base
    run_mode = 'rt'
    Ts = SAMPLE_TIME
    name = 'environment'

    def __init__(self, visualization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = Dynamic2DWorld_Base(name='world', parent=self)
        self.visualization_type = visualization

        if self.visualization_type == 'babylon':
            self.visualization = BabylonVisualization(fetch_function=self.getVisualizationSample, *args, **kwargs)
        elif self.visualization_type == 'simple2d':
            self.visualization = Simple2DVisualization(fetch_function=self.getVisualizationSample, *args, **kwargs)
        else:
            self.visualization = None

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

    # === ACTIONS ======================================================================================================
    def _init(self, *args, **kwargs):
        ...
        # Set the world configuration in the babylon visualization if needed
        if self.visualization is not None:
            self.visualization.setWorldConfig(self.world.generateWorldConfig())
            self.visualization.start()
            setBabylonSettings(status='')

    def _action_entry(self, *args, **kwargs):
        super()._action_entry(*args, **kwargs)

    def _action_step(self, *args, **kwargs):

        pass

    def action_input(self, *args, **kwargs):
        pass

    def action_controller(self, *args, **kwargs):
        pass

    def action_visualization(self, *args, **kwargs):
        ...
        # if self.visualization == 'babylon':
        #     sample = self.getVisualizationSample()
        #     self.babylon.sendSample(sample)

    def action_output(self, *args, **kwargs):
        pass

    def action_world(self, *args, **kwargs):
        pass