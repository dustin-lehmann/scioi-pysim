import scioi_py_core.core.world as world
import scioi_py_core.core.dynamics as dynamics
import scioi_py_core.core.spaces as spaces


# TODO: Make the agent group
class AgentGroup(world.WorldObjectGroup):
    ...


class Agent(world.WorldObject):
    agent_id: int
    agent_group: AgentGroup

    def __init__(self, name: str = None, world: world.World = None,
                 space: spaces.Space = None, agent_id: int = 1, *args, **kwargs):
        super().__init__(name=name, world=world, group=None, space=space, *args, **kwargs)

        self.collision.settings.check = True
        self.collision.settings.collidable = True

        self.agent_id = agent_id  # TODO: Change this, so that the id is either given by the world or group + dynamical assignment

    def _getParameters(self):
        params = super()._getParameters()
        params['agent_id'] = self.agent_id
        return params

    def _onAdd_callback(self):
        super()._onAdd_callback()
        self.world.addAgent(self)


class DynamicAgent(Agent, dynamics.DynamicWorldObject):

    def __init__(self, name: str = None, world: world.World = None, space: spaces.Space = None, agent_id: int = 1,
                 *args, **kwargs):
        super().__init__(name=name, world=world, space=space, agent_id=agent_id, *args, **kwargs)


        pass
