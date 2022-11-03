import dataclasses
import enum
import threading
import time
from abc import ABC, abstractmethod
from typing import Union
import simpy


class Action:
    """
    - an Action is a wrapper around a function that gets executed in its corresponding Phase by the Scheduler

    """
    function: callable  # Function that is going to be called
    actions: dict[str, 'Action']
    parameters: dict  # Default arguments that are going to be set
    lambdas: dict  # List of lambdas executed before the function call
    object: 'ScheduledObject'  # Object this action is associated with
    parent: 'Action'

    frequency: int  # TODO Default 1. This action is only executed every <frequency> calls of the corresponding phase
    priority: int  # TODO Default 1. Not used yet

    # TODO: One shot actions

    name: str  # Trivial name for easier debugging

    def __init__(self, function: callable = None, parent: 'Action' = None, parameters=None, lambdas=None,
                 object: 'ScheduledObject' = None,
                 frequency: int = 1, priority: int = 1, name: str = ""):

        if lambdas is None:
            lambdas = {}
        if parameters is None:
            parameters = {}

        self.actions = {}
        self.parameters = parameters
        self.lambdas = lambdas

        self.function = function
        self.frequency = frequency
        self.priority = priority

        self._parent = None

        if name is None:
            if function is not None:
                name = f"{function.__name__}_{id(self)}"
            else:
                name = f"{id(self)}"

        self.name = name
        self.parent = parent

        # if self.parent is not None:
        #     self.parent.registerAction(self)

        self.object = None
        if object is not None:
            object.registerAction(self)

    # == PROPERTIES ====================================================================================================
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value: 'Action'):

        if value is not None:
            value.registerAction(self)

    # == METHODS =======================================================================================================
    def run(self, *args, **kwargs):
        """
        Run the function with the provided arguments and the stored default arguments
        :param args:
        :param kwargs:
        :return:
        """

        # Debug: Check for the calltree argument
        if 'calltree' in kwargs and kwargs['calltree']:
            try:
                print(f"Action: \"{self.name}\" Object: \"{self.object.name}\": {type(self.object).__name__} ")
            except AttributeError:
                print(f"Action: \"{self.name}\" Object: None")

        # Run the function
        lambdas_exec = {key: value() for (key, value) in self.lambdas.items()}
        if self.function is not None:
            ret = self.function(*args, **{**self.parameters, **kwargs, **lambdas_exec})

        # Run the child actions
        for name, actions in self.actions.items():
            actions(*args, **{**self.parameters, **kwargs, **lambdas_exec})

    def registerAction(self, action):
        """
        Registers the given action or list of actions in the phase.
        :param action: Action or List -> Action(s) to be added
        :return:
        """
        if isinstance(action, list):
            for ac in action:
                assert (isinstance(ac, Action))
                self.registerAction(ac)

        elif isinstance(action, Action):

            assert (action.parent is None)
            action._parent = self

            if action.name in self.actions:
                name = f"{action.name}_{id(action)}"
            else:
                name = action.name

            self.actions[name] = action
            if action.parent is not self:
                action.parent = self

            # Sort the dict by priority
            self.actions = {k: v for k, v in sorted(self.actions.items(), key=lambda item: item[1].priority)}

    def removeAction(self, action):
        """
        Removes the given action or list of actions from the phase.
        :param action: Action or list -> Action(s) to be removed
        :return:
        """
        if isinstance(action, list):
            for ac in action:
                assert (isinstance(ac, Action))
                self.removeAction(ac)

        elif isinstance(action, Action):
            del (self.actions[action.name])
            action.parent = None

            # Sort the dict by priority
            self.actions = {k: v for k, v in sorted(self.actions.items(), key=lambda item: item[1].priority)}

    # == BUILT-INS =====================================================================================================
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


# ======================================================================================================================
@dataclasses.dataclass
class SchedulingData:
    """
    Stores all scheduling related data for a scheduled object
    """

    _object: 'ScheduledObject'
    _parent: 'ScheduledObject' = None
    tick: int = 0  # Internal tick counter
    _t: float = 0
    _Ts: float = 0
    children: list['ScheduledObject'] = dataclasses.field(default_factory=list)  # Child objects
    events: dict = dataclasses.field(default_factory=list)  # Events
    actions: dict[str, Action] = dataclasses.field(default_factory=dict)
    _tick_global: int = 0

    # TODO this needs Ts_global and a local Ts as soon as I allow frequencies of actions

    @property
    def tick_global(self):
        if self.parent is not None:
            return self.parent.scheduling.tick_global
        else:
            return self._tick_global

    @tick_global.setter
    def tick_global(self, value):
        if self.parent is None:
            self._tick_global = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value: 'ScheduledObject'):
        self._parent = value
        if self._parent is not None:
            self._parent.registerChild(self._object)

    @property
    def t(self):
        return self.tick_global * self.Ts

    @t.setter
    def t(self, value):
        if self.parent is None:
            self._t = value

    @property
    def Ts(self):
        if self.parent is not None:
            return self.parent.scheduling.Ts
        else:
            return self._Ts

    @Ts.setter
    def Ts(self, value):
        if self.parent is None:
            self._Ts = value


# ======================================================================================================================
class ScheduledObject(ABC):
    scheduling: SchedulingData
    name: str

    def __init__(self, name=None, parent=None, *args, **kwargs):
        self.scheduling = SchedulingData(_object=self)

        if name is None:
            name = f"{type(self).__name__}_{id(self)}"

        if not hasattr(self, 'name'):
            self.name = name

        action_entry = Action(name='_entry', function=self._action_entry)
        action_exit = Action(name='_exit', function=self._action_exit)
        action_start = Action(name='_start', function=self._action_start)
        action_pause = Action(name='_pause', function=self._action_pause)
        action_stop = Action(name='_stop', function=self._action_stop)
        action_init = Action(name='_init', function=self._init)

        self.registerAction(action_entry)
        self.registerAction(action_exit)
        self.registerAction(action_start)
        self.registerAction(action_pause)
        self.registerAction(action_stop)
        self.registerAction(action_init)

        self.scheduling.parent = parent

    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================
    def registerCallback(self, event, callback, parameters):
        # TODO
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def registerAction(self, action):
        assert (isinstance(action, Action))
        assert (action.object is None)
        assert (action.name not in self.scheduling.actions)
        self.scheduling.actions[action.name] = action
        action.object = self

    # ------------------------------------------------------------------------------------------------------------------
    def registerChild(self, child: 'ScheduledObject'):
        # Register the default actions
        child.scheduling.actions['_entry'].parent = self.scheduling.actions['_entry']
        child.scheduling.actions['_exit'].parent = self.scheduling.actions['_exit']
        child.scheduling.actions['_start'].parent = self.scheduling.actions['_start']
        child.scheduling.actions['_pause'].parent = self.scheduling.actions['_pause']
        child.scheduling.actions['_stop'].parent = self.scheduling.actions['_stop']
        child.scheduling.actions['_init'].parent = self.scheduling.actions['_init']
        self.scheduling.children.append(child)

    def deregisterChild(self, child: 'ScheduledObject'):
        child.scheduling.parent = None
        child.scheduling.actions['_entry'].parent = None
        child.scheduling.actions['_exit'].parent = None
        child.scheduling.actions['_start'].parent = None
        child.scheduling.actions['_pause'].parent = None
        child.scheduling.actions['_stop'].parent = None
        child.scheduling.actions['_init'].parent = None

        self.scheduling.actions['_entry'].removeAction(child.scheduling.actions['_entry'])
        self.scheduling.actions['_exit'].removeAction(child.scheduling.actions['_exit'])
        self.scheduling.actions['_start'].removeAction(child.scheduling.actions['_start'])
        self.scheduling.actions['_pause'].removeAction(child.scheduling.actions['_pause'])
        self.scheduling.actions['_stop'].removeAction(child.scheduling.actions['_stop'])
        self.scheduling.actions['_init'].removeAction(child.scheduling.actions['_init'])

        self.scheduling.children.remove(child)

    # == DEFAULT ACTIONS ===============================================================================================
    def _action_entry(self, *args, **kwargs):
        pass

    def _action_exit(self, *args, **kwargs):
        pass

    def _action_start(self, *args, **kwargs):
        pass

    def _action_pause(self, *args, **kwargs):
        pass

    def _action_stop(self, *args, **kwargs):
        pass

    @abstractmethod
    def _init(self):
        pass


# ======================================================================================================================
@dataclasses.dataclass
class SimpyEvents:
    exit: simpy.Event = None
    halt: simpy.Event = None
    timeout: simpy.Event = None
    resume: simpy.Event = None
    reset: simpy.Event = None


# ======================================================================================================================
class Scheduler:
    action: Action
    simpy_env: simpy.Environment
    simpy_events: SimpyEvents
    mode: str  # 'fast' or 'rt'. Default: 'rt'
    Ts: float
    # env: 'Environment'
    tick: int
    steps: int
    thread: threading.Thread

    # === INIT =========================================================================================================
    def __init__(self, action, mode: str = 'rt', Ts: float = 1):
        self.action = action
        self.mode = mode
        self.Ts = Ts
        self.simpy_events = SimpyEvents()
        self.thread = None

        self._init()

        self.args = []
        self.kwargs = {}

    # === PROPERTIES ===================================================================================================
    # === METHODS ======================================================================================================
    def run(self, steps=None, thread=False, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs

        if thread:
            self.thread = threading.Thread(target=self.run, args=[steps, False])
            self.thread.start()

        if steps is not None:
            self.simpy_events.timeout = self.simpy_env.timeout(steps - 1)

        self.simpy_env.process(self._run())
        # TODO: Try to register KeyboardInterrupt
        while True:
            try:
                self.simpy_env.run(
                    until=(
                        simpy.AnyOf(self.simpy_env,
                                    [self.simpy_events.timeout, self.simpy_events.exit, self.simpy_events.halt])))
            except KeyboardInterrupt:
                self.simpy_events.exit.succeed()

            if self.simpy_events.exit.processed:
                # self.state = SchedulerState.EXITED
                # self.exit()
                break
            elif self.simpy_events.timeout.processed:
                # self.state = SchedulerState.EXITED
                print("Simulation Exit (Timeout)")
                break
            elif self.simpy_events.halt.processed:
                # self.state = SchedulerState.HALTED
                self.simpy_events.halt = self.simpy_env.event()
                print("Simulation halted")
                raise Exception("Not implemented yet!")
            elif self.simpy_events.resume.processed:
                # self.state = SchedulerState.RUNNING
                print("Simulation resumed")
                raise Exception("Not implemented yet!")

    # === PRIVATE METHODS ==============================================================================================
    def _init(self):
        if self.mode == 'rt':
            self.simpy_env = simpy.RealtimeEnvironment(factor=self.Ts, strict=False)
        elif self.mode == 'fast':
            self.simpy_env = simpy.Environment()

        self.simpy_events.reset = self.simpy_env.event()
        self.simpy_events.exit = self.simpy_env.event()
        self.simpy_events.halt = self.simpy_env.event()
        self.simpy_events.timeout = self.simpy_env.event()
        self.simpy_events.resume = self.simpy_env.event()

        self.tick = 0
        self.steps = 0

    # ------------------------------------------------------------------------------------------------------------------
    def _run(self):
        while True:
            self._step(*self.args, **self.kwargs)
            yield self.simpy_env.timeout(1)

    # ------------------------------------------------------------------------------------------------------------------
    def _step(self, *args, **kwargs):
        self.action(*args, **kwargs)


def registerActions(object: ScheduledObject, parent_action: Action, default_actions: bool = False,
                    exclude: list = None):
    # TODO: Add exclude list

    for name, act in object.scheduling.actions.items():
        if not default_actions and not (name.startswith("_")):
            act.parent = parent_action
