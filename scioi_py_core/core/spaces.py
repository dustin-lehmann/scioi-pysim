import copy as cp
import numpy as np

from .. import utils as utils


class Dimension:
    """

    """
    name: str  # Name of the dimension, such as "x" or "y"
    unit: str  # Name of the unit
    limits: list  # Upper and lower limit
    wrapping: bool  # If wrapping is true, then the dimension will wrap around the upper or lower limit
    discretization: float  # lowest increment of the value of the dimension
    error_on_limit: bool  # If TRUE an error will be generated if the value violates the limits
    complex: bool  # If TRUE, it allows for complex numbers
    shape: tuple  # Dimension of the dimension, like (n,m) for an n x m dimension
    type: type

    def __init__(self, name, discretization=0, limits=None, wrapping=False, unit=None, error_on_limit=False,
                 complex=False, dimension=(1, 1), type=float):
        self.name = name
        self.discretization = discretization
        self.limits = limits
        self.wrapping = wrapping
        self.unit = unit
        self.error_on_limit = error_on_limit

        self.complex = complex
        self.shape = dimension
        self.type = type

    # == METHODS =======================================================================================================
    def project(self, value):
        if value is None:
            return None

        if self.limits is not None:
            if self.wrapping:
                value = utils.utils.wrap(self.limits, value)
            else:
                if not utils.utils.inInterval(self.limits, value):
                    if self.error_on_limit:
                        raise Exception("Value violates dimension constraints")
                    else:
                        value = utils.utils.stickToInterval(self.limits, value)

        if self.discretization > 0:
            value = self.discretization * round(value / self.discretization)

        return value

    def zero(self):
        if self.shape == (1, 1):
            return 0
        elif self.type == np.ndarray:
            return np.zeros(shape=self.shape)

    def empty(self):
        if self.shape == (1, 1):
            return None
        else:
            return None

    def __repr__(self):
        return f"{self.name}"


class Space:
    dimensions: list[Dimension]
    mappings: list
    name: str

    def __init__(self, dimensions: (int, list)):
        if isinstance(dimensions, int):
            self.dimensions = []
            for i in range(0, dimensions):
                self.dimensions.append(Dimension(name='dim_' + str(i)))

        elif isinstance(dimensions, list) and all(isinstance(elem, str) for elem in dimensions):
            self.dimensions = []
            for dimension in dimensions:
                self.dimensions.append(Dimension(name=dimension))
        elif isinstance(dimensions, list) and all(isinstance(elem, Dimension) for elem in dimensions):
            self.dimensions = []
            for dimension in dimensions:
                self.dimensions.append(dimension)

        self.mappings = []

    # == METHODS =======================================================================================================
    def zeros(self):
        out = State(space=self)
        for dim in self.dimensions:
            value = dim.zero()
            out[dim.name] = value
        return out

    def ones(self):
        return State(space=self, value=np.ones(self.dof))

    # ------------------------------------------------------------------------------------------------------------------
    def map(self, state, force=True):

        if state is None:
            return None

        cond_1 = isinstance(state, list) and all([isinstance(elem, (int, float)) for elem in state]) and len(
            state) == self.dof
        cond_2 = isinstance(state, np.ndarray) and state.shape == (self.dof,)
        cond_3 = isinstance(state, State)
        cond_4 = (isinstance(state, int) or isinstance(state, float)) and self.dof == 1

        assert (cond_1 or cond_2 or cond_3 or cond_4)

        new_state = State(space=self)

        if isinstance(state, (list, np.ndarray)):
            for i, dimension in enumerate(self.dimensions):
                new_state[i] = dimension.project(state[i])
        elif isinstance(state, State):
            if state.space == self:
                for i, dimension in enumerate(self.dimensions):
                    new_state[i] = dimension.project(state[i])
            else:
                _map = next((mapping for mapping in self.mappings if state.space in mapping), None)
                if _map is not None:
                    new_state = _map.map(state)
                else:
                    if force and len(state) == self.dof:
                        for i, dimension in enumerate(self.dimensions):
                            new_state[i] = dimension.project(state[i])
                    else:
                        return None
        elif isinstance(state, (int, float)):
            new_state[0] = self.dimensions[0].project(state)
            # new_state[0] = dimension.project(state[i])
        else:
            return None
        return new_state

    # -----------------------------------------------------------------------------------------------------------------
    def project(self, state):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def add_mapping(self, mapping):
        assert (isinstance(mapping, Mapping) or (
                isinstance(mapping, list) and all([isinstance(elem, Mapping) for elem in mapping])))

        if mapping not in self.mappings:
            self.mappings.append(mapping)

    # ------------------------------------------------------------------------------------------------------------------
    def has_mapping(self, space):
        if space == self:
            return True
        elif any([elem for elem in self.mappings if space in elem]):
            return True
        elif self.dof == space.dof and all(
                [self.dimensions[i].name == space.dimensions[i].name for i in range(0, self.dof)]):
            return True
        return False

    # == PROPERTIES ====================================================================================================
    @property
    def dof(self):
        return len(self.dimensions)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def dimension_names(self):
        out = []
        for dim in self.dimensions:
            out.append(dim.name)
        return out

    # == BUILT INS =====================================================================================================

    def __repr__(self):
        return f"{self.dimensions}"


# ======================================================================================================================
class State:
    space: Space
    value: list

    def __init__(self, space, value=None):

        self.space = space
        self.value = []
        self.empty()

        if value is not None:
            self.set(value)

    # == PROPERTIES ====================================================================================================
    @property
    def T(self):
        if all([dim.type == float for dim in self.space.dimensions]):
            return np.transpose(self.value)
        else:
            return None

    @property
    def _names(self):
        return [dimension.name for dimension in self.space.dimensions]

    # == METHODS =======================================================================================================
    def set(self, value):
        # value = np.atleast_1d(np.asarray(value))
        assert len(value) == len(self.space.dimensions)
        for i in range(0, len(self.value)):
            self[i] = value[i]

    def empty(self):
        self.value = []
        for i, dim in enumerate(self.space.dimensions):
            self.value.append(dim.empty())

    # == PRIVATE METHODS ===============================================================================================
    def _index(self, key):
        idx = next((idx for idx, element in enumerate(self.space.dimensions) if element.name == key), None)
        if idx is None:
            raise Exception("Index not found")
        return idx

    # == BUILT-INS =====================================================================================================
    def __setitem__(self, key, value):
        assert (isinstance(key, (int, str)))
        if isinstance(key, int):
            self.value[key] = self.space.dimensions[key].project(value)
        if isinstance(key, str):
            self.value[self._index(key)] = self.space.dimensions[self._index(key)].project(value)

    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, item):
        assert (isinstance(item, (int, str, slice)))
        if isinstance(item, int):
            return self.value[item]
        elif isinstance(item, str):
            return self.value[self._index(item)]
        elif isinstance(item, slice):
            return self.value[item]

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == len(self.space.dimensions):
            other = np.asarray(other)
            self_copy.set(self_copy.value + other)
        elif isinstance(other, np.ndarray) and other.shape == self.value.shape:
            self_copy.set(self_copy.value + other)
        elif isinstance(other, State) and self.space.dof == other.space.dof:
            self_copy.set([x + y for x, y in zip(self.value, other.value)])
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __radd__(self, other):
        return self.__add__(other)

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == len(self.space.dimensions):
            other = np.asarray(other)
            self_copy.set(self_copy.value - other)
        elif isinstance(other, np.ndarray) and other.shape == self.value.shape:
            self_copy.set(self_copy.value - other)
        elif isinstance(other, State) and other.space.dof == self.space.dof:
            self_copy.set(self_copy.value - other.value)
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __rsub__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == len(self.space.dimensions):
            other = np.asarray(other)
            self_copy.val = other - self_copy.val
        elif isinstance(other, np.ndarray) and other.shape == self.value.shape:
            self_copy.val = other - self_copy.val
        elif isinstance(other, State) and other.space.dof == self.space.dof:
            self_copy.val = other.value - self_copy.val
        elif isinstance(other, (int, float)) and len(self.space.dimensions) == 1:
            self_copy.val = other - self_copy.val
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, (int, float)):
            self_copy.set([val * other for val in self_copy.value])
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __rmul__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, (int, float)):
            self_copy.set([val * other for val in self_copy.value])

        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __matmul__(self, other):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def __rmatmul__(self, other):
        assert (isinstance(other, np.ndarray))
        assert (other.shape[1] == len(self.space.dimensions))

        if other.shape[0] == other.shape[1]:  # quadratic matrix. Retains original state structure
            self_copy = cp.copy(self)
            self_copy.value = np.asarray(other @ self.value)
            return self_copy
        else:
            self_copy = cp.copy(self)
            self_copy.value = np.asarray(other @ self.value)
            return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __iter__(self):
        for i in self.value:
            yield i
        return

    # ------------------------------------------------------------------------------------------------------------------
    def __len__(self):
        return len(self.value)

    # ------------------------------------------------------------------------------------------------------------------
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ == "matmul":
            return self.__rmatmul__(inputs[0])
        elif ufunc.__name__ == 'subtract':
            return self.__rsub__(inputs[0])
        elif ufunc.__name__ == 'multiply':
            return self.__mul__(inputs[0])
        else:
            raise Exception("Not implemented yet!")

    # ------------------------------------------------------------------------------------------------------------------
    def __copy__(self):
        return self.__deepcopy__(self)

    # ------------------------------------------------------------------------------------------------------------------
    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        copy = type(self)(value=cp.copy(self.value), space=self.space)
        return copy
        # memo[id(self)] = copy
        # copy.space = self.space

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        out_str = '['
        for i, name in enumerate(self._names):
            out_str = out_str + "{:s}: {}, ".format(name, self.value[i])
        out_str = out_str[:-2] + ']'
        return out_str


class Mapping:
    space_from: Space
    space_to: Space

    def __init__(self, space_from: Space, space_to: Space, mapping, inverse=None):
        self.space_from = space_from
        self.space_to = space_to
        self.mapping = mapping
        self.inverse = inverse

        self.space_from.add_mapping(self)
        self.space_to.add_mapping(self)

    # == METHODS =======================================================================================================
    def map(self, state):
        assert (isinstance(state, State) and (state.space == self.space_from or state.space == self.space_to))
        if state.space == self.space_from:
            return State(space=self.space_to, value=self.mapping(state))
        elif state.space == self.space_to:
            return State(space=self.space_from, value=self.inverse(state))

    # == PRIVATE METHODS ===============================================================================================
    def __contains__(self, item):
        if isinstance(item, Space):
            if item == self.space_from or item == self.space_to:
                return True
        elif isinstance(item, State):
            if item.space == self.space_from or item.space == self.space_to:
                return True
        return False
