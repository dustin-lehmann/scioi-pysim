import time
from abc import ABC, abstractmethod

from ..core import scheduling as scheduling
from ..core import world as world
from ..utils.babylon import getBabylonSettings


class Environment(scheduling.ScheduledObject):
    scheduler: scheduling.Scheduler
    world: world.World
    action_step: scheduling.Action

    run_mode: str
    Ts: float

    # TODO put these in a separate dataclass?
    '''
    - step action
    -- step entry
    -- step input
    -- step output
    -- step exit
    
    also actions like:
    -- start
    -- pause
    -- stop
    -- error
    -- init
    
    more specific environments get more actions like
    -- hardware manager
    -- sensor reading
    -- world
    -- visualization    
    '''

    # === INIT =========================================================================================================
    def __init__(self, run_mode: str = None, Ts: float = None, *args, **kwargs):
        super().__init__()

        if run_mode is not None:
            self.run_mode = run_mode

        if Ts is not None:
            self.Ts = Ts

        # TODO: is it ok to do this here?. Probably some if it should be put somewhere else
        self.action_step = scheduling.Action(name='step', object=self)
        self.scheduling.actions['_entry'].parent = self.action_step
        self.scheduling.actions['_entry'].priority = 0
        self.scheduling.actions['_exit'].parent = self.action_step
        self.scheduling.actions['_exit'].priority = 1000

        self.scheduler = scheduling.Scheduler(action=self.action_step, mode=self.run_mode, Ts=self.Ts)
        pass

    # === PROPERTIES ===================================================================================================

    # === METHODS ======================================================================================================
    def step(self, *args, **kwargs):
        self.scheduling.actions['step'].run(*args, **kwargs)

    def start(self, *args, **kwargs):
        self.scheduler.run(*args, **kwargs)

    def init(self, *args, **kwargs):
        self.scheduling.actions['_init'].run(*args, **kwargs)

    def getVisualizationSample(self):
        sample = {
            'time': self.scheduling.tick_global * self.Ts,
            'world': self.world.getVisualizationSample(),
            'settings': getBabylonSettings()
        }
        return sample
    def getSample(self):
        ...

    # === PRIVATE METHODS ==============================================================================================
    @abstractmethod
    def _action_step(self):
        pass

    def _step(self):
        # TODO: Not like this. those actions are added to an action that runs
        #  once a step which is given to the scheduler. only like this can I make the tree
        time1 = time.time()
        self.scheduling.actions['entry']()
        self.scheduling.actions['step']()
        self.scheduling.actions['exit']()
        time2 = time.time()
        print((time2 - time1) * 1000)

    def _action_entry(self, *args, **kwargs):
        super()._action_entry()
        self.scheduling.tick += 1
        self.scheduling.tick_global = self.scheduling.tick

    def _action_start(self, *args, **kwargs):
        super()._action_start()
        self.scheduling.tick = 0
        self.scheduling.tick_global = 0
