import scioi_pysim.core as core

xy_coord_space = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x', discretization=1),
                                                    core.spaces.Dimension(name='y', discretization=1)])

xy_config_space = xy_coord_space

xy_single_integrator_ss = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x'),
                                                             core.spaces.Dimension(name='y')])

xy_single_integrator_ss.add_mapping(core.spaces.SpaceMapping(xy_single_integrator_ss, xy_config_space,
                                                             mapping=lambda state: [state['x'], state['y']],
                                                             inverse=lambda config: [config['x'], config['y']]))


# XY_Single_Integrator_Dynamics ########################################################################################
class XY_Single_Integrator_Dynamics(core.dynamics.Dynamics):

    def __init__(self):
        self.state_space = xy_single_integrator_ss
        self.n = 2
        self.p = 2
        self.q = 2
        super().__init__()

    def _dynamics(self, state, input):
        x = state + input
        return x

    def _output_function(self, state):
        return state


# XY_Agent #############################################################################################################
class XY_Agent(core.agents.DynamicAgent):

    def __init__(self, name: str = None, state=None, world=None):
        super().__init__(dynamics=XY_Single_Integrator_Dynamics(),
                         configuration_space=xy_config_space,
                         name=name,
                         world=world)

        if state is not None:
            self.dynamics.state = state

    def _register(self):
        super()._register()
        print("Register Agent!")

    def _sim_init(self):
        super()._sim_init()
        print("init agent")

    def _step_entry(self, *args, **kwargs):
        super()._step_entry(*args, **kwargs)

    def _action_input(self, *args, **kwargs):
        # print("HELLO")
        super()._action_input(*args, **kwargs)


# XY_World #############################################################################################################
class XY_World(core.world.DynamicWorld):

    def __init__(self):
        super().__init__(coordinate_space=xy_coord_space, configuration_space=xy_config_space)

    def _sim_init(self):
        # print("Init World")
        super()._sim_init()

    def _step_entry(self, *args, **kwargs):
        # print("World Step entry")
        super()._step_entry(*args, **kwargs)

    def _action_post(self):
        super()._action_post()
        self.sim.log_value('test', 5)



