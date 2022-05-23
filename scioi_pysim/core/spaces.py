import copy as cp
from typing import List, Dict, Callable, Union
import numpy as np
from . import utils


# Dimension ############################################################################################################
class Dimension:
    name: str  # optional
    unit: str  # optional
    limits: None
    wrapping: bool
    discretization: int

    # == INIT ==========================================================================================================
    def __init__(self, name=None, discretization=0, limits=None, wrapping=False, unit=None):
        self.limits = limits
        self.unit = unit
        self.name = name
        self.wrapping = wrapping
        self.discretization = discretization

    # == METHODS =======================================================================================================
    def project(self, val):
        val = cp.copy(val)
        violation = False
        if self.limits is not None:
            if val < self.limits[0]:
                if self.wrapping:
                    val = utils.wrap(self.limits, val)
                else:
                    val = self.limits[0]
                    violation = True
            if val > self.limits[1]:
                if self.wrapping:
                    val = utils.wrap(self.limits, val)
                else:
                    val = self.limits[1]
                    violation = True

        if self.discretization != 0:
            val = self.discretization * round(val / self.discretization)

        return val


# StateSpace ###########################################################################################################
class StateSpace:
    dof: int  # Dimensions of the state space
    dimensions: list[Dimension]  # Dimensions
    mappings: list

    # == INIT ==========================================================================================================
    def __init__(self, dof: int = None, dimensions=None, prefix=None) -> object:
        if dimensions is None:
            assert (dof is not None)
            self.dimensions = []
            self.dof = dof
            for i in range(0, self.dof):
                if prefix is not None:
                    self.dimensions.append(Dimension(name=prefix + '_' + str(i)))
                else:
                    self.dimensions.append(Dimension(name='dim_' + str(i)))
        else:
            self.dimensions = []
            assert (isinstance(dimensions, list))
            self.dof = len(dimensions)
            for dimension in dimensions:
                assert (type(dimension) == Dimension)
                self.dimensions.append(dimension)

        self.mappings = []

    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================
    def map(self, state, force=True):

        if state is None:
            return None

        cond_1 = isinstance(state, list) and all([isinstance(elem, (int, float)) for elem in state]) and len(
            state) == self.dof
        cond_2 = isinstance(state, np.ndarray) and state.shape == (self.dof,)
        cond_3 = isinstance(state, State)
        if not (cond_1 or cond_2 or cond_3):
            a = 2
        assert (cond_1 or cond_2 or cond_3)

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
        else:
            return None
        return new_state

    # ------------------------------------------------------------------------------------------------------------------
    def derive(self, dimensions: list, mapping: Callable, inverse: Callable):
        assert (isinstance(dimensions, list))
        new_dimensions = []
        for dimension in dimensions:
            if isinstance(dimension, str):
                if any([dim.name == dimension for dim in self.dimensions]):
                    dim = next(dim for dim in self.dimensions if dim.name == dimension)
                    new_dimensions.append(dim)
                else:
                    new_dimensions.append(Dimension(name=dimension))
            elif isinstance(dimension, Dimension):
                new_dimensions.append(dimension)

        derived_ss = StateSpace(new_dimensions)
        SpaceMapping(self, derived_ss, mapping, inverse)
        return derived_ss

    # ------------------------------------------------------------------------------------------------------------------
    def add_mapping(self, mapping):
        assert (isinstance(mapping, SpaceMapping) or (
                isinstance(mapping, list) and all([isinstance(elem, SpaceMapping) for elem in mapping])))

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

    # ------------------------------------------------------------------------------------------------------------------
    def zeros(self):
        return State(space=self, val=np.zeros(self.dof))

    # ------------------------------------------------------------------------------------------------------------------
    def ones(self):
        return State(space=self, val=np.ones(self.dof))

    # ------------------------------------------------------------------------------------------------------------------
    def __deepcopy__(self, memodict={}):
        return self


# STATE ################################################################################################################
class State:
    space: StateSpace
    val: np.ndarray

    # == INIT ==========================================================================================================
    def __init__(self, space=None, val=None):

        if space is None and val is not None:
            self.space = StateSpace(dof=len(val))
        elif space is not None:
            self.space = space
        else:
            raise Exception

        self.val = np.zeros(self.space.dof)
        if val is not None:
            self.set(val)
        else:
            self.set(np.zeros(self.space.dof))

    # == PROPERTIES ====================================================================================================
    @property
    def names(self):
        return [dimension.name for dimension in self.space.dimensions]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def T(self):
        return np.transpose(self.val)

    # == METHODS =======================================================================================================
    def set(self, val):
        val = np.atleast_1d(np.asarray(val))
        assert (val.shape == (self.space.dof,))
        for i in range(0, len(self.val)):
            self[i] = val[i]

    # ------------------------------------------------------------------------------------------------------------------
    def map(self, space: StateSpace, force=False):
        if space == self.space:
            return self
        # check if there is any map to this space
        # _map = next((_map for _map in self.space.mappings if space in _map), None)
        return space.map(self, force=True)

    # == PRIVATE METHODS ===============================================================================================
    def __repr__(self):
        out_str = '['
        for i, name in enumerate(self.names):
            out_str = out_str + "{:s}: {:.2f}, ".format(name, self.val[i])
        out_str = out_str[:-2] + ']'
        return out_str

    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, item):
        assert (isinstance(item, (int, str, slice)))
        if isinstance(item, int):
            return self.val[item]
        elif isinstance(item, str):
            return self.val[self._index(item)]
        elif isinstance(item, slice):
            return self.val[item]

    # ------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, key, value):
        assert (isinstance(key, (int, str)))
        if isinstance(key, int):
            self.val[key] = self.space.dimensions[key].project(value)
        if isinstance(key, str):
            self.val[self._index(key)] = self.space.dimensions[self._index(key)].project(value)

    # ------------------------------------------------------------------------------------------------------------------
    def _index(self, key):
        idx = next((idx for idx, element in enumerate(self.space.dimensions) if element.name == key), None)
        if idx is None:
            raise Exception("Index not found")
        return idx

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == self.space.dof:
            other = np.asarray(other)
            self_copy.set(self_copy.val + other)
        elif isinstance(other, np.ndarray) and other.shape == self.val.shape:
            self_copy.set(self_copy.val + other)
        elif isinstance(other, State) and self.space.dof == other.space.dof:
            self_copy.set([x + y for x, y in zip(self.val, other.val)])
            # self_copy.val = self_copy.val + other.val
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __radd__(self, other):
        return self.__add__(other)

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == self.space.dof:
            other = np.asarray(other)
            self_copy.set(self_copy.val - other)
        elif isinstance(other, np.ndarray) and other.shape == self.val.shape:
            self_copy.set(self_copy.val - other)
        elif isinstance(other, State) and other.space.dof == self.space.dof:
            self_copy.set(self_copy.val - other.val)
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __rsub__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, list) and len(other) == self.space.dof:
            other = np.asarray(other)
            self_copy.val = other - self_copy.val
        elif isinstance(other, np.ndarray) and other.shape == self.val.shape:
            self_copy.val = other - self_copy.val
        elif isinstance(other, State) and other.space.dof == self.space.dof:
            self_copy.val = other.val - self_copy.val
        elif isinstance(other, (int, float)) and self.space.dof == 1:
            self_copy.val = other - self_copy.val
        else:
            raise Exception
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, (int, float)):
            self_copy.val = [val * other for val in self_copy.val]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __rmul__(self, other):
        self_copy = cp.copy(self)
        if isinstance(other, (int, float)):
            self_copy.val = [val * other for val in self_copy.val]
        return self_copy

    # ------------------------------------------------------------------------------------------------------------------
    def __matmul__(self, other):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def __rmatmul__(self, other):
        assert (isinstance(other, np.ndarray))
        assert (other.shape[1] == self.space.dof)

        if other.shape[0] == other.shape[1]:  # quadratic matrix. Retains original state structure
            self_copy = cp.copy(self)
            self_copy.val = np.asarray(other @ self.val)
            return self_copy
        else:
            val = np.asarray(other @ self.val)
            return State(val=val)

    # ------------------------------------------------------------------------------------------------------------------
    def __iter__(self):
        for i in self.val:
            yield i
        return

    # ------------------------------------------------------------------------------------------------------------------
    def __len__(self):
        return len(self.val)

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
    def __deepcopy__(self, memodict={}):
        copy = type(self)(val=cp.copy(self.val), space=self.space)
        return copy
        # memo[id(self)] = copy
        # copy.space = self.space


# SpaceMapping #########################################################################################################
class SpaceMapping:
    space_from: StateSpace
    space_to: StateSpace

    # == INIT ==========================================================================================================
    def __init__(self, space_from, space_to, mapping, inverse):
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
            return State(space=self.space_to, val=self.mapping(state))
        elif state.space == self.space_to:
            return State(space=self.space_from, val=self.inverse(state))

    # == PRIVATE METHODS ===============================================================================================
    def __contains__(self, item):
        if isinstance(item, StateSpace):
            if item == self.space_from or item == self.space_to:
                return True
        elif isinstance(item, State):
            if item.space == self.space_from or item.space == self.space_to:
                return True
        return False


# Default Spaces #######################################################################################################

# CS_R2 ################################################################################################################
class CS_R2(StateSpace):
    # == INIT ==========================================================================================================
    def __init__(self):
        super().__init__(dimensions=[Dimension(name='x'), Dimension(name='y')])


# CS_R2_DISC ###########################################################################################################
class CS_R2_DISC(StateSpace):
    # == INIT ==========================================================================================================
    def __init__(self, discretization=1):
        super().__init__(dimensions=[Dimension(name='x', discretization=discretization),
                                     Dimension(name='y', discretization=discretization)])


# CS_R3 ################################################################################################################
class CS_R3(StateSpace):
    # == INIT ==========================================================================================================
    def __init__(self):
        super().__init__(dimensions=[Dimension(name='x'), Dimension(name='y'), Dimension(name='z')])


# CS_R3_DISC ###########################################################################################################
class CS_R3_DISC(StateSpace):
    # == INIT ==========================================================================================================
    def __init__(self, discretization=1):
        super().__init__(dimensions=[Dimension(name='x', discretization=discretization),
                                     Dimension(name='y', discretization=discretization),
                                     Dimension(name='z', discretization=discretization)])
