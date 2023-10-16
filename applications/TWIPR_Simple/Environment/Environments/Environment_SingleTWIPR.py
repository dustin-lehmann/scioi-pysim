from applications.TWIPR_Simple.Environment.Environments.environment_base import EnvironmentBase
from applications.TWIPR_Simple.Environment.EnvironmentTWIPR_objects import TWIPR_DynamicAgent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.utils.joystick.joystick import Joystick
from scioi_py_core.utils.joystick.keyboard import ArrowKeys

class Environment_SingleTWIPR(EnvironmentBase):
    agent1: TWIPR_DynamicAgent
    obstacle1: CuboidObstacle_3D
    keys: ArrowKeys

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_DynamicAgent(agent_id=1, name='Agent 1', world=self.world, speed_control=True)
        self.joystick = Joystick()

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        self.agent1.input = [-1*self.joystick.axis[1], -4*self.joystick.axis[2]]
        pass


class Environment_SingleTWIPR_KeyboardInput(EnvironmentBase):
    agent1: TWIPR_DynamicAgent
    obstacle1: CuboidObstacle_3D
    keys: ArrowKeys

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_DynamicAgent(agent_id=1, name='Agent 1', world=self.world, speed_control=True)
        self.keys = ArrowKeys()

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        self.agent1.input = [2*(self.keys.keys['UP']-self.keys.keys['DOWN']), 5*(self.keys.keys['LEFT']-self.keys.keys['RIGHT'])]
        pass



