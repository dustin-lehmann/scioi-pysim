from dataclasses import dataclass, field
from typing import Callable, Dict, List, ClassVar, Union
from types import FunctionType, MethodType
import copy as cp
import pickle
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
import simpy
import threading

from . import utils
from scioi_pysim import core as core


def _wrapper(fun, **kwargs):
    return lambda *a, **aa: fun(*a, **aa, **kwargs)


# Action ###############################################################################################################
class Action:
    position: int
    description: str

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, position=0, description=None):
        self.position = position
        self.description = description

    # ------------------------------------------------------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        self.run()

    # ------------------------------------------------------------------------------------------------------------------
    def run(self):
        pass


# Phase ################################################################################################################
class Phase(Action):
    actions: Dict[str, Action]
    sort_id: str
    type = 'Phase'

    # == INIT ==========================================================================================================
    def __init__(self, position=0, action=None, description="", sort_id=None):
        super().__init__(position, description)
        self.actions = {}
        self.sort_id = sort_id

        if action is not None:
            self.set_actions(action)

    # == METHODS =======================================================================================================
    def set_actions(self, actions):
        # Delete all actions
        self.actions = {}
        if isinstance(actions, Dict):
            for (description, action) in actions.items():
                if isinstance(action, (Function, FunctionType)):
                    self.add_function(function=action, description=description)
                elif isinstance(action, Phase):
                    self.add_phase(action, description=description)
        elif isinstance(actions, Phase):
            self.add_phase(actions)
        elif isinstance(actions, Function):
            self.add_function(actions)
        elif isinstance(actions, Callable):
            self.add_function(Function(function=actions))

    # ------------------------------------------------------------------------------------------------------------------
    def add_function(self, function, position=None, arguments=None, lambdas=None, description=None, sort_id=None):
        if isinstance(function, Function):
            if position is None:
                position = function.position
            if description is None:
                description = function.description

            if description in self.actions.keys():
                count = 2
                while description + "_" + str(count) in self.actions.keys():
                    count = count + 1
                description = description + "_" + str(count)
            self.actions[description] = function

        elif isinstance(function, (FunctionType, MethodType)):
            if description is None:
                description = function.__name__
            if position is None:
                position = len(self.actions)

            # find a name for the function thats not already taken
            if description in self.actions.keys():
                count = 2
                while description + "_" + str(count) in self.actions.keys():
                    count = count + 1
                description = description + "_" + str(count)

            self.actions[description] = Function(function, arguments, lambdas, position, description, sort_id)
        self.sort_actions()
        return self.actions[description]

    # ------------------------------------------------------------------------------------------------------------------
    def add_phase(self, phase, description=None, position=None):
        if isinstance(phase, Phase):
            if description is not None:
                phase.description = description
            if position is not None:
                phase.position = position
            if phase.description in self.actions.keys():
                count = 2
                while phase.description + "_" + str(count) in self.actions.keys():
                    count = count + 1
                description = phase.description + "_" + str(count)
            else:
                description = phase.description

            self.actions[description] = phase
            self.sort_actions()
            return self.actions[description]

    # ------------------------------------------------------------------------------------------------------------------
    def remove_action(self, action=None, params: dict = None, params_mode='and', invert=False, recursive=False):
        # Explicit removal
        if action is not None:
            if not isinstance(action, list):
                action = [action]

            for _action in action:
                for description, __action in list(self.actions.items()):
                    if isinstance(_action, str) and _action == description:
                        del self.actions[description]
                    elif isinstance(_action, (Phase, Function)) and _action == __action:
                        del self.actions[description]
                    elif isinstance(__action, Phase) and _action is not __action and recursive:
                        __action.remove_action(action, params, params_mode, invert, recursive)

        # Implicit removal
        elif params is not None:
            for description, action in list(self.actions.items()):
                delete = []
                for key, condition in params.items():
                    if hasattr(action, key):
                        _delete = (getattr(action, key) == condition) ^ invert  # XOR between the logical value
                        # of the condition and the invert
                        delete.append(_delete)

                if delete:
                    if params_mode == 'and' and all(delete):
                        del self.actions[description]
                    elif params_mode == 'or' and any(delete):
                        del self.actions[description]

                if isinstance(action, Phase) and description in self.actions.keys() and recursive:
                    action.remove_action(None, params, params_mode, invert, recursive)

    # ------------------------------------------------------------------------------------------------------------------
    def clear(self):
        self.actions = {}

    # ------------------------------------------------------------------------------------------------------------------
    def sort_actions(self):
        self.actions = {k: v for k, v in sorted(self.actions.items(), key=lambda item: item[1].position)}

    # ------------------------------------------------------------------------------------------------------------------
    def run(self):
        # Sort the actions
        for action in self.actions.values():
            action()

    # == PRIVATE METHODS ===============================================================================================
    def __getitem__(self, key):
        return self.actions[key]


# Function #############################################################################################################
class Function(Action):
    fun: Callable
    lambdas: Dict
    function_name: str
    function_id: int
    sort_id: int
    type = 'Function'

    # == INIT ==========================================================================================================
    def __init__(self, function, arguments: dict = None, lambdas=None, position=0, description=None, sort_id=None):
        super().__init__(position, description)
        if arguments is None:
            arguments = {}
        if lambdas is None:
            lambdas = {}
        self.function_id = id(function)
        self.fun = _wrapper(function, **arguments)

        self.lambdas = lambdas
        self.arguments = arguments
        self.function_name = function.__name__
        self.sort_id = sort_id

        if description is None:
            self.description = function.__name__
        else:
            self.description = description

    # == METHODS =======================================================================================================
    def run(self, *args, **kwargs):
        lambdas_exec = {key: value() for (key, value) in self.lambdas.items()}
        kwargs = {**kwargs, **lambdas_exec}
        self.fun(*args, **kwargs)


# LogEntry #############################################################################################################
class LogEntry:

    # == INIT ==========================================================================================================
    def __init__(self):
        self._list = []
        self.signals = []

    # == METHODS =======================================================================================================
    def clear(self):
        self.__dict__ = {}
        self._list = []

    # == PRIVATE METHODS ===============================================================================================
    def __setitem__(self, key, value):
        if isinstance(key, str):
            self.__dict__[key] = cp.copy(value)
            self.signals.append(key)
        elif isinstance(key, int):
            utils.set_list(self._list, key, value)
            self.__dict__[str(key)] = cp.copy(value)

    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.__dict__[key]
        if isinstance(key, int):
            return self._list[key]


# Log ##################################################################################################################
class Log:
    entries: list[LogEntry]
    Ts: float

    # == INIT ==========================================================================================================
    def __init__(self, Ts: float = 1):

        self.Ts = Ts
        self.entries = []

    # == METHODS =======================================================================================================
    def append(self, item: LogEntry):
        self.entries.append(cp.copy(item))

    # ------------------------------------------------------------------------------------------------------------------
    def save(self, filename):
        # make the data ready to pickle
        data = []
        for entry in self.entries:
            entry_serial = {}
            for s in entry.signals:
                signal = entry[s]
                if isinstance(signal, core.spaces.State):
                    entry_serial[s] = list(signal)
            data.append(entry_serial)

        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    # ------------------------------------------------------------------------------------------------------------------
    def timeseries(self, key):
        # TODO: not finished!
        vals = []
        for entry in self.entries:
            if utils.hasattrd(entry, key):
                vals.append(utils.getattrd(entry, key))
            else:
                vals.append(None)
        ts = Timeseries(vals, Ts=self.Ts)
        return ts

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, key):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def clear(self):
        self.entries = []

    # == PRIVATE METHODS ===============================================================================================
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.entries[item]
        elif isinstance(item, slice):
            return self.entries[item]
        elif isinstance(item, str):
            if item in self.__dict__.keys():
                return self.__dict__[item]
            else:
                # Get this item from every log entry
                output = []
                for entry in self.entries:
                    if hasattr(entry, item):
                        output.append(entry[item])
                    else:
                        output.append(None)
                return output

    # ------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.entries[key] = value
        elif isinstance(key, str):
            self.__dict__[key] = value

    # ------------------------------------------------------------------------------------------------------------------
    def __len__(self):
        return len(self.entries)


# Timeseries ###########################################################################################################
class Timeseries:
    data: List
    # len: int
    type: ClassVar
    shape: tuple
    Ts: float
    name: str
    unit: str

    # == INIT ==========================================================================================================
    def __init__(self, data=None, default=None, length=None, Ts: float = 1, name=None, unit=None):

        self.data = []
        if data is not None:
            if isinstance(data, list):
                for elem in data:
                    self.append(elem)
            elif isinstance(data, Timeseries):
                self.data = cp.copy(data.data)
            elif isinstance(data, np.ndarray):
                self.data = list(cp.copy(data))
            else:
                raise Exception
        else:
            if length is not None:
                self.data = [default] * length

        self.Ts = Ts
        self.name = name
        self.unit = unit

    # == PROPERTIES ====================================================================================================
    @property
    def type(self):
        if not self.data:
            return None
        first_item = next(item for item in self.data if item is not None)
        return type(first_item)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def data_shape(self):
        if not self.data:
            return None
        first_item = next(item for item in self.data if item is not None)
        if self.type in [int, float, np.float64]:
            return 1
        elif self.type == np.ndarray:
            return first_item.shape

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def t(self):
        return [elem * self.Ts for elem in range(len(self))]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def T(self):
        return self

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def len(self):
        return len(self)

    # == METHODS =======================================================================================================
    def append(self, val, copy=False):
        if copy:
            base = cp.copy(self)
        else:
            base = self
        if isinstance(val, list):
            for element in val:
                base.data.append(cp.copy(element))
        elif isinstance(val, Timeseries):
            base.data.append(val.data)
        elif isinstance(val, (int, float, np.ndarray)):
            base.data.append(cp.copy(val))
        else:
            base.data.append(cp.copy(val))
        return base

    # ------------------------------------------------------------------------------------------------------------------
    def compatible(self, other):
        if isinstance(other, Timeseries) and len(self) == len(other):
            return True

        if isinstance(other, list) and len(self) == len(other):
            return True

        if isinstance(other, np.ndarray) and (self.shape == 1 and (len(other.shape) == 1 or other.shape[1] == 1)):
            return True

        return False

    # ------------------------------------------------------------------------------------------------------------------
    def list(self):
        return cp.copy(self.data)

    # ------------------------------------------------------------------------------------------------------------------
    def array(self):
        return np.asarray(cp.copy(self.data))

    # ------------------------------------------------------------------------------------------------------------------
    def resample(self, Ts, copy=False):
        if copy:
            ts = cp.copy(self)
        else:
            ts = self

        new_time = np.arange(start=ts.t[0], stop=ts.t[-1] + Ts, step=Ts)
        new_data = list(np.interp(x=new_time, xp=ts.t, fp=ts.data))

        ts.data = new_data
        ts.Ts = Ts

        return ts

    # ------------------------------------------------------------------------------------------------------------------
    def plot(self, title=None, hold=False, log=False, **kwargs):
        if hold:
            plt.figure(plt.gcf())
        else:
            plt.figure()

        plt.plot(self.t, self.data, marker='o', markersize=2, linestyle=':', **kwargs)
        if self.name is not None:
            plt.ylabel(self.name + ' [' + str(self.unit) + ']')
        if self.Ts != 1:
            plt.xlabel('time [s]')
        else:
            plt.xlabel('step [-]')
        if title is not None:
            plt.title(title)
        if not hold:
            plt.grid()
            plt.show()

    # ------------------------------------------------------------------------------------------------------------------
    def fun(self, function, copy=True):
        if copy:
            self_copy = cp.copy(self)
        else:
            self_copy = self

        for i, element in enumerate(self_copy.data):
            self_copy.data[i] = function(element)

        return self_copy

    # == PRIVATE METHODS ===============================================================================================
    def __len__(self):
        return len(self.data)

    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str) and self.type == core.spaces.State:
            data = [elem[key] for elem in self.data]
            new_ts = Timeseries(data=data, Ts=self.Ts)
            return new_ts
        elif isinstance(key, slice):
            return self.data[key]

    # ------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, key, value):
        _len = len(self)
        if isinstance(key, slice):
            for i in range(0, key.stop - _len):
                self.data.append(None)
            for index, i in enumerate(range(key.start, key.stop)):
                if isinstance(value, list):
                    self.data[i] = value[index]
                elif isinstance(value, np.ndarray):
                    raise Exception("Not implemented")
                else:
                    self.data[i] = value
        else:
            for i in range(0, key - _len + 1):
                self.data.append(None)
            self.data[key] = cp.copy(value)

    # ------------------------------------------------------------------------------------------------------------------
    def __iter__(self):
        for i in self.data:
            yield i
        return

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        assert (self.compatible(other))
        self_copy = cp.copy(self)
        for i, element in enumerate(self_copy.data):
            try:
                self_copy.data[i] = self_copy.data[i] + other[i]
            except TypeError:
                if self_copy.data[i] is None or other[i] is None:
                    self_copy.data[i] = None

        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __radd__(self, other):
        assert (self.compatible(other))
        return self.__add__(other)

    # ------------------------------------------------------------------------------------------------------------------
    def __rsub__(self, other):
        assert (self.compatible(other))
        self_copy = cp.copy(self)
        for i, element in enumerate(self_copy.data):
            self_copy.data[i] = other[i] - self_copy.data[i]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        assert (self.compatible(other))
        self_copy = cp.copy(self)
        for i, element in enumerate(self_copy.data):
            self_copy.data[i] = self_copy.data[i] - other[i]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other):
        assert (isinstance(other, (int, float)))
        self_copy = cp.copy(self)
        self_copy.data = [element * other for element in self_copy.data]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __rmul__(self, other):
        assert (isinstance(other, (int, float)))
        self_copy = cp.copy(self)
        self_copy.data = [element * other for element in self_copy.data]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __matmul__(self, other):
        raise Exception("Not implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def __rmatmul__(self, other):
        assert (isinstance(other, np.ndarray))
        assert (other.shape[1] == len(self))
        self_copy = cp.copy(self)
        self_copy.data = list(other @ self.data)
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return ''.join(str(self.data))

    # ------------------------------------------------------------------------------------------------------------------
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ == "matmul":
            return self.__rmatmul__(inputs[0])
        elif ufunc.__name__ == 'subtract':
            return self.__rsub__(inputs[0])
        elif ufunc.__name__ == 'multiply':
            return self.__mul__(inputs[0])
        elif ufunc.__name__ == 'degrees':
            return self.fun(ufunc)
        else:
            raise Exception("Not implemented yet!")

    def __copy__(self):
        return Timeseries(data=cp.copy(self.data), name=self.name, unit=self.unit, Ts=self.Ts)


# SimFlag ########################################################################################################
class SimFlag:
    id: str
    data: None
    raised: bool

    def __init__(self, id, data=None):
        self.id = id
        self.data = data
        self.raised = False

    def __call__(self, *args, **kwargs):
        self.raised = True
        if args:
            self.data = args[0]

    def clear(self):
        self.raised = False


# SimObjectFlags #######################################################################################################
@dataclass
class SimObjectFlags:
    error: SimFlag = SimFlag('error')
    halt: SimFlag = SimFlag('halt')
    exit: SimFlag = SimFlag('exit')


# SimObjectActions #####################################################################################################
class SimObjectActions:
    actions: dict
    n: int

    def __init__(self):
        self.actions = {}
        self.n = 0

    def __iter__(self):
        actions = sorted(self.actions.items(), key=lambda item: item[1].position)
        yield from actions

    def __next__(self):
        actions = sorted(self.actions.items(), key=lambda item: item[1].position)

        action = actions[self.n][1]
        self.n = self.n + 1
        return action

    def __getitem__(self, item):
        return self.actions[item]

    def __setitem__(self, key, value):
        assert (isinstance(value, Action))
        self.actions[key] = value

    def _update_next(self):
        action = next(self)
        action()

    def reset(self):
        self.n = 0

    def __len__(self):
        return len(self.actions)

    def run(self):
        actions = sorted(self.actions.items(), key=lambda item: item[1].position)
        actions = [action[1] for action in actions]

        for action in actions:
            action()


# SimObjectData ########################################################################################################
@dataclass
class SimObjectData:
    step: int = 0
    step_global: int = 0
    Ts: float = 1
    Ts_global: float = 0
    log_entry: LogEntry = field(default_factory=LogEntry)
    log: Log = field(default_factory=Log)
    flags: SimObjectFlags = field(default_factory=SimObjectFlags)
    childs: list['SimObject'] = field(default_factory=list)
    parent: 'SimObject' = None
    actions: 'SimObjectActions' = field(default_factory=SimObjectActions)

    # action: Action = None
    # phases: dict = field(default_factory=dict)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def t(self):
        return self.Ts * self.step

    # ------------------------------------------------------------------------------------------------------------------
    def get_childs(self, recursive=True) -> List['SimObject']:
        out = []
        for child in self.childs:
            out.append(child)
            if recursive and child.sim.childs:
                out.extend(child.sim.get_childs())
        return out

    # ------------------------------------------------------------------------------------------------------------------
    def log_value(self, key, value):
        self.log_entry[key] = value

    # ------------------------------------------------------------------------------------------------------------------


# SimObject ############################################################################################################
class SimObject:
    sim: SimObjectData

    # == INIT ==========================================================================================================
    def __init__(self, Ts: float = 1):
        self.sim = SimObjectData()
        self.sim.Ts = Ts
        self._create()

    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================
    # ------------------------------------------------------------------------------------------------------------------
    def _register_child(self, obj: 'SimObject'):
        self.sim.childs.append(obj)
        obj.sim.parent = self
        obj._register()

    # ------------------------------------------------------------------------------------------------------------------
    def _deregister_child(self, obj: 'SimObject'):
        self.sim.childs.remove(obj)
        obj.sim.parent = None
        obj._deregister()

    # ------------------------------------------------------------------------------------------------------------------

    # == DEFAULT ACTIONS ===============================================================================================
    def _create(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _delete(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _attach(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _reset(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _detach(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _sim_init(self):
        # print("Init!")
        if self.sim.Ts == -1:
            self.sim.Ts = self.sim.parent.sim.Ts
        if self.sim.parent is not None:
            if self.sim.Ts is not self.sim.parent.sim.Ts:
                raise Exception
        childs = self.sim.get_childs(recursive=False)
        for child in childs:
            child._sim_init()

    # ------------------------------------------------------------------------------------------------------------------
    def _update(self, sequential=True):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _reset(self):
        self.sim.step = 0
        self.sim.log.clear()
        self.sim.log_entry = LogEntry()

    # ------------------------------------------------------------------------------------------------------------------
    def _step_entry(self, *args, **kwargs):
        # print("Entry!")
        if 'step_global' in kwargs.keys():
            self.sim.step_global = kwargs['step_global']

        self.sim.step = self.sim.step + 1
        childs = self.sim.get_childs(recursive=False)
        for child in childs:
            child._step_entry(*args, **kwargs)
        self.sim.log_entry = LogEntry()

    # ------------------------------------------------------------------------------------------------------------------
    def _step_exit(self):
        self.sim.log.append(self.sim.log_entry)
        childs = self.sim.get_childs(recursive=False)
        for child in childs:
            child._step_exit()
        self.sim.log_entry = None

    # ------------------------------------------------------------------------------------------------------------------
    def _halt(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _finish(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _start(self):
        print("Start!")
        childs = self.sim.get_childs(recursive=False)
        for child in childs:
            child._start()

    # ------------------------------------------------------------------------------------------------------------------
    def _register(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _deregister(self):
        pass

class ScheduledEvent:
    obj: SimObject
    step: int  # Step at which the event is taking place
    base: str  # 'local' oder 'global'
    fun: Action  # Function to be executed

    def __init__(self):
        pass

    def check_condition(self):
        pass


########################################################################################################################
class SimulatorState(Enum):
    UNINITIALIZED = 0
    RUNNING = 1
    HALTED = 2
    EXITED = 3
    INITIALIZED = 4
    ERROR = 5


########################################################################################################################
@dataclass
class EnvEvents:
    exit: simpy.Event = None
    halt: simpy.Event = None
    timeout: simpy.Event = None
    resume: simpy.Event = None
    reset: simpy.Event = None


########################################################################################################################
@dataclass
class SimFlags:
    exit: bool = False
    halt: bool = False
    resume: bool = False
    reset: bool = False

    def reset_flags(self):
        self.exit = False
        self.halt = False
        self.resume = False
        self.reset = False


########################################################################################################################
class Simulator:
    objects: List[SimObject]
    state: SimulatorState
    sim_step: int
    mode: str

    Ts: float

    log: Log
    log_entry: LogEntry

    env: simpy.Environment
    env_events: EnvEvents

    sched_events: None  # Scheduled events
    cond_events: None  # Conditional events

    flags: SimFlags

    # == INIT ==========================================================================================================
    def __init__(self, Ts=1, mode='fast', objects: Union[list, SimObject] = None):
        """Initializes the Simulator and sets the initial values. Also calls all "_init()" functions of all simulated
        objects

        Parameters
        ----------
        Ts: float
            timestep of the simulator
        mode: str
            Can be 'rt' for real-time simulation, 'accelerated' for faster simulation and 'fast'
            for fast-time simulation
        objects: list
            List of top-level objects that gets directly simulated by the Simulator, i.e. their update action is
            directly called

        Returns
        ----------
        -
        """
        # -- Input processing -----------------
        self.Ts = Ts
        self.mode = mode

        if objects is None:
            self.objects = []
        else:
            if isinstance(objects, SimObject):
                objects = [objects]
            self.objects = objects

        # -- Field defaults -------------------
        self.log = Log()
        self.log_entry = LogEntry()
        self.env_events = EnvEvents()
        self.state = SimulatorState.UNINITIALIZED
        self.sim_step = 0
        self.flags = SimFlags()

    # == PROPERTIES ====================================================================================================
    @property
    def t(self):
        return self.sim_step * self.Ts

    # == METHODS =======================================================================================================
    def init(self):
        """Initializes the Simulator and sets the initial values. Also calls all "_init()" functions of all simulated
        objects

        Parameters
        ----------
        -

        Returns
        ----------
        -
        """
        self.sim_step = 0
        self.flags.reset_flags()
        self.log = Log()
        self.log_entry = LogEntry()
        self._init_env()

        # Call all init functions of the sim_objects
        for obj in self.objects:
            obj._sim_init()

        self.state = SimulatorState.INITIALIZED

    # ------------------------------------------------------------------------------------------------------------------
    def step(self):
        """ Performs one simulation step

        Parameters
        ----------
        -
        Returns
        ----------
        -
        """
        if self.state is not SimulatorState.INITIALIZED and self.state is not SimulatorState.RUNNING:
            raise Exception

        # Execute the Start Events if this is the first time step
        if self.sim_step == 0:
            for obj in self.objects:
                obj._start()

        # Increment the own step counter
        self.sim_step += 1

        # Execute the entry events:
        for obj in self.objects:
            obj._step_entry(step_global=self.sim_step)

        # Simulate own phases
        self._phase_input()

        self._phase_p1()

        self._phase_objects()

        self._phase_p2()

        self._phase_output()

        self._phase_logging()

        self._step_exit()

        # Check Flags
        all_objs = self._get_all_objs()

        for obj in all_objs:
            if obj.sim.flags.halt.raised:
                obj.sim.flags.halt.clear()
                self.env_events.halt.succeed()

            if obj.sim.flags.error.raised:
                obj.sim.flags.error.clear()
                self.env_events.exit.succeed()

            if obj.sim.flags.exit.raised:
                obj.sim.flags.exit.clear()
                self.env_events.exit.succeed()

        if self.flags.exit:
            self.env_events.exit.succeed()

    # ------------------------------------------------------------------------------------------------------------------
    def register(self, sim_object: SimObject):
        """Registers given objects(s) in the list of simulation objects

        Parameters
        ----------
        sim_object: SimObject
            The object that is registered as a sim object in the simulator

        Returns
        ----------
        -
        """
        if not isinstance(sim_object, list):
            sim_object = [sim_object]

        for obj in sim_object:
            if obj not in self.objects:
                self.objects.append(obj)
                obj.sim.step_global = self.sim_step
                obj.sim.Ts_global = self.Ts
                obj._register()

    # ------------------------------------------------------------------------------------------------------------------
    def remove(self, sim_object: SimObject):
        """Removes given objects(s) from the list of simulation objects

        Parameters
        ----------
        sim_object: SimObject
            The object that is removed

        Returns
        ----------
        -
        """
        if not isinstance(sim_object, list):
            sim_object = [sim_object]

        for obj in sim_object:
            if obj in self.objects:
                self.objects.remove(obj)

    # ------------------------------------------------------------------------------------------------------------------
    def run(self, time=None, steps=None, thread=False):

        # if the simulation is running in a separate Thread, call this function again, with thread=False
        if thread:
            thr = threading.Thread(target=self.run, args=[time, steps, False])
            thr.start()
            return

        if self.state is not SimulatorState.INITIALIZED and self.state is not SimulatorState.RUNNING:
            raise Exception

        if time is not None and steps is not None:
            raise Exception

        if time is not None:
            steps = time / self.Ts - 1
        if steps is not None:
            self.env_events.timeout = self.env.timeout(steps-1)

        self.env.process(self._run())
        self.state = SimulatorState.RUNNING
        while True:
            self.env.run(
                until=(simpy.AnyOf(self.env, [self.env_events.timeout, self.env_events.exit, self.env_events.halt])))

            if self.env_events.exit.processed:
                self.state = SimulatorState.EXITED
                print("Simulation exit")
                break
            elif self.env_events.timeout.processed:
                self.state = SimulatorState.EXITED
                print("Simulation Exit (Timeout)")
                break
            elif self.env_events.halt.processed:
                self.state = SimulatorState.HALTED
                self.env_events.halt = self.env.event()
                print("Simulation halted")
                raise Exception("Not implemented yet!")
            elif self.env_events.resume.processed:
                self.state = SimulatorState.RUNNING
                print("Simulation resumed")
                raise Exception("Not implemented yet!")

        print("Simulation exit!")
        self.user_sim_exit()

    # == PRIVATE METHODS ===============================================================================================
    def _init_env(self):
        """Initializes the Simpy Environment

        Parameters
        ----------
        -
        Returns
        ----------
        -
        """
        if self.mode == 'rt':
            self.env = simpy.RealtimeEnvironment(factor=self.Ts, strict=False)
        elif self.mode == 'accelerated':
            raise Exception("Not implemented yet!")
        elif self.mode == 'fast':
            self.env = simpy.Environment()

        self.env_events.reset = self.env.event()
        self.env_events.exit = self.env.event()
        self.env_events.halt = self.env.event()
        self.env_events.timeout = self.env.event()
        self.env_events.resume = self.env.event()

    # ------------------------------------------------------------------------------------------------------------------
    def _run(self):
        while True:
            self.step()
            yield self.env.timeout(1)

    # ------------------------------------------------------------------------------------------------------------------
    def _get_all_objs(self):
        objs = []
        for obj in self.objects:
            objs.append(obj)
            objs.extend(obj.sim.get_childs(recursive=True))
        return objs

    # ------------------------------------------------------------------------------------------------------------------
    def _phase_input(self, *args, **kwargs):
        self.user_input(*args, **kwargs)

    def _phase_p1(self, *args, **kwargs):
        self.user_p1(*args, **kwargs)

    def _phase_objects(self, *args, **kwargs):

        for obj in self.objects:
            obj.sim.actions.run()

    def _phase_p2(self, *args, **kwargs):
        self.user_p2(*args, **kwargs)

    def _phase_output(self, *args, **kwargs):
        self.user_output(*args, **kwargs)

    def _phase_logging(self, *args, **kwargs):
        self.user_logging(*args, **kwargs)

    def _step_exit(self):
        for obj in self.objects:
            obj._step_exit()

    # ------------------------------------------------------------------------------------------------------------------
    def user_input(self, *args, **kwargs):
        pass

    def user_logging(self, *args, **kwargs):
        pass

    def user_p1(self, *args, **kwargs):
        pass

    def user_p2(self, *args, **kwargs):
        pass

    def user_output(self, *args, **kwargs):
        pass

    def user_sim_exit(self, *args, **kwargs):
        pass