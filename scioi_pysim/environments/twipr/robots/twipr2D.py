import scioi_pysim.core as core
from scioi_pysim.dynamics.twipr import TWIPR_2D_StateSpace

TWIPR_2D_ConfigSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='s'),
                                                          core.spaces.Dimension(name='theta')])

TWIPR_2D_World_CoordinateSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='s'),
                                                                    core.spaces.Dimension(name='z')])

TWIPR_2D_World_ConfigSpace = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='s'),
                                                                core.spaces.Dimension(name='theta'),
                                                                core.spaces.Dimension(name='z')])

TWIPR_2D_World_CoordinateSpace.add_mapping(core.spaces.SpaceMapping(TWIPR_2D_World_CoordinateSpace, TWIPR_2D_World_CoordinateSpace,
                                                          mapping=lambda config: [config[0], config[2]], inverse=None))

TWIPR_2D_StateSpace.add_mapping(core.spaces.SpaceMapping(TWIPR_2D_StateSpace, TWIPR_2D_ConfigSpace,
                                                         mapping=lambda state: [state[0], state[2]],
                                                         inverse=lambda config: [config[0], 0, config[1], 0]))

TWIPR_2D_ConfigSpace.add_mapping(core.spaces.SpaceMapping(TWIPR_2D_ConfigSpace, TWIPR_2D_World_ConfigSpace,
                                                          mapping=lambda config: [config[0], config[1], 0],
                                                          inverse=None))

TWIPR_2D_StateSpace.add_mapping(core.spaces.SpaceMapping(TWIPR_2D_StateSpace, TWIPR_2D_World_ConfigSpace,
                                                         mapping=lambda state: [state[0], state[2], 0],
                                                         inverse=lambda config: [config[0], 0, config[1], 0]))


class TWIPR_2D_Agent(core.agents.DynamicAgent):
    pass
