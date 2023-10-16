import abc
import copy as cp
from math import pi

import numpy as np
import qmt

import scioi_py_core.utils.utils as utils
import scioi_py_core.utils.orientations as orientation_utils


def dumper(obj):
    if hasattr(obj, 'serialize'):
        return obj.serialize()
    else:
        return obj.__dict__


class StateValue(abc.ABC):
    name: str
    value: object

    def __init__(self, name: str = None):
        if not hasattr(self, 'name'):
            self.name = name

    def set(self, value):
        ...

    def project(self, value):
        ...

    def copy(self):
        return self._copy()

    def _copy(self):
        return cp.copy(self)

    def zero(self):
        ...

    def _zero(self):
        ...

    @abc.abstractmethod
    def serialize(self):
        ...


# ======================================================================================================================
class ScalarValue(StateValue):
    unit: str
    limits: list = None
    wrapping: bool = True
    discretization: float = 0.0
    value: float

    def __init__(self, name: str = None, value: float = None, limits: list = None, wrapping: bool = True,
                 discretization: float = 0):
        super().__init__(name)
        if not hasattr(self, 'limits'):
            self.limits = limits
        if not hasattr(self, 'wrapping'):
            self.wrapping = wrapping
        if not hasattr(self, 'discretization'):
            self.discretization = discretization

        self.zero()

        if value is not None:
            self.set(value)

    def serialize(self):
        return self.value

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value):
        if value is None:
            self.value = None
            return

        if isinstance(value, ScalarValue):
            value = value.value

        value = float(value)

        if self.limits is not None:
            if self.wrapping:
                value = utils.wrap(self.limits, value)
            else:
                if not utils.inInterval(self.limits, value):
                    value = utils.stickToInterval(self.limits, value)

        if self.discretization > 0:
            value = self.discretization * round(value / self.discretization)

        self.value = value

    # ------------------------------------------------------------------------------------------------------------------
    def none(self):
        self.set(None)

    # ------------------------------------------------------------------------------------------------------------------
    def one(self):
        self.set(1)

    # ------------------------------------------------------------------------------------------------------------------
    def zero(self):
        self.set(self._zero())

    # ------------------------------------------------------------------------------------------------------------------
    def add(self, other):
        new_value = self.copy()

        if isinstance(other, ScalarValue):
            new_value.set(self.value + other.value)
        elif isinstance(other, (int, float)):
            new_value.set(self.value + other)

        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def sub(self, other):
        new_value = self.copy()

        if isinstance(other, ScalarValue):
            new_value.set(self.value - other.value)
        elif isinstance(other, (int, float)):
            new_value.set(self.value - other)

        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def mul(self, other):
        new_value = self.copy()

        if isinstance(other, ScalarValue):
            new_value.set(self.value * other.value)
        elif isinstance(other, (int, float)):
            new_value.set(self.value * other)

        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def imul(self, other):

        if isinstance(other, ScalarValue):
            self.set(self.value * other.value)
        elif isinstance(other, (int, float)):
            self.set(self.value * other)

        return self

    # ------------------------------------------------------------------------------------------------------------------
    def iadd(self, other):
        if isinstance(other, ScalarValue):
            self.set(self.value + other.value)
        elif isinstance(other, (int, float)):
            self.set(self.value + other)
        return self

    # ------------------------------------------------------------------------------------------------------------------
    def isub(self, other):
        if isinstance(other, ScalarValue):
            self.set(self.value - other.value)
        elif isinstance(other, (int, float)):
            self.set(self.value - other)
        return self

    # ------------------------------------------------------------------------------------------------------------------
    def div(self, other):
        return self._div(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def idiv(self, other):
        return self._div(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def _zero(self):
        return 0

    # ------------------------------------------------------------------------------------------------------------------
    def _div(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        if isinstance(other, ScalarValue):
            new_value.set(self.value / other.value)
        elif isinstance(other, (int, float)):
            new_value.set(self.value / other)

        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def _rdiv(self, other):

        new_value = self.copy()

        if isinstance(other, ScalarValue):
            new_value.set(other.value / self.value)
        elif isinstance(other, (int, float)):
            new_value.set(other / self.value)

        return new_value

    # === BUILT-IN =====================================================================================================
    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __isub__(self, other):
        return self.isub(other)

    def __iadd__(self, other):
        return self.iadd(other)

    def __mul__(self, other):
        return self.mul(other)

    def __rtruediv__(self, other):
        return self._rdiv(other)

    def __truediv__(self, other):
        return self.div(other)

    def __itruediv__(self, other):
        return self.idiv(other)

    def __imul__(self, other):
        return self.imul(other)

    def __rmul__(self, other):
        return self.mul(other)

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f"{self.value}"


# ======================================================================================================================
class VectorValue(StateValue):
    value: np.ndarray
    shape: tuple
    names: list
    limits: list
    discretization: list
    len: int

    def __init__(self, name: str = None, value: (list, np.ndarray) = None, shape: tuple = None, names: list = None,
                 limits: list = None, discretization: list = None, wrapping: (list, bool) = True):
        super().__init__(name)

        if not hasattr(self, 'limits'):
            self.limits = limits
        if not hasattr(self, 'wrapping'):
            self.wrapping = wrapping
        if not hasattr(self, 'discretization'):
            self.discretization = discretization
        if not hasattr(self, 'names'):
            self.names = names
        if not hasattr(self, 'shape'):
            self.shape = shape

        assert (self.shape is not None and len(self.shape) == 1)
        self.len = self.shape[0]
        self.value = np.ndarray(shape=self.shape)
        self.zero()

        if self.names is None:
            self.names = []
            for i in range(0, self.len):
                self.names.append(f"dim_{i}")

        if value is not None:
            self.set(value)

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value, index: (int, str) = None):
        if index is None:
            if isinstance(value, (list, np.ndarray)):
                for i in range(0, self.len):
                    self._setItem(value[i], i)
            elif isinstance(value, VectorValue):
                for i in range(0, self.len):
                    self._setItem(value.value[i], i)
        elif isinstance(index, int):
            self._setItem(value, index)
        elif isinstance(index, str):
            dim_index = self.names.index(index)
            self._setItem(value, dim_index)

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, index: (int, str) = None):
        if index is None:
            return self.value
        elif isinstance(index, int):
            return self.value[index]
        elif isinstance(index, str):
            dim_index = self.names.index(index)
            return self.value[dim_index]

    # ------------------------------------------------------------------------------------------------------------------
    def zero(self):
        self.set(self._zero())

    # ------------------------------------------------------------------------------------------------------------------
    def _zero(self):
        return np.zeros(self.shape)

    # ------------------------------------------------------------------------------------------------------------------
    def _setItem(self, value, index):
        if hasattr(value, 'value'):
            value = value.value
        value = float(value)

        if self.limits is not None:
            wrap = False
            if self.wrapping is not None:
                if isinstance(self.wrapping, bool):
                    wrap = self.wrapping
                elif isinstance(self.wrapping, list):
                    wrap = self.wrapping[index]
            if wrap:
                value = utils.wrap(self.limits[index], value)
            else:
                if not utils.inInterval(self.limits[index], value):
                    value = utils.stickToInterval(self.limits[index], value)

        if self.discretization is not None:
            if self.discretization[index] is not None:
                if self.discretization[index] > 0:
                    value = self.discretization[index] * round(value / self.discretization[index])

        self.value[index] = value

    # ------------------------------------------------------------------------------------------------------------------
    def add(self, other):
        return self._add(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def iadd(self, other):
        return self._add(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def sub(self, other):
        return self._sub(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def isub(self, other):
        return self._sub(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def mul(self, other):
        return self._mul(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def div(self, other):
        return self._div(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def idiv(self, other):
        return self._div(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def imul(self, other):
        return self._mul(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def _add(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()
        # Case 1: Other value is also a vector in the same dimension
        if isinstance(other, VectorValue) and other.shape == self.shape:
            new_value.set(self.value + other.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list) and len(other) == self.len:
            new_value.set(self.value + np.asarray(other))
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(self.value + other)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _sub(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()
        # Case 1: Other value is also a vector in the same dimension
        if isinstance(other, VectorValue) and other.shape == self.shape:
            new_value.set(self.value - other.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list) and len(other) == self.len:
            new_value.set(self.value - np.asarray(other))
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(self.value - other)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _mul(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        # Case 1: Other Value is a ScalarValue
        if isinstance(other, ScalarValue):
            new_value.set(self.value * other.value)
            return new_value

        # Case 2: Other Value is an int or float
        if isinstance(other, (int, float)):
            new_value.set(self.value * other)
            return new_value

        # Case 3: Other is a matrix
        if isinstance(other, np.ndarray) and other.shape == (self.len, self.len):
            new_value.set(other @ self.value)
            return new_value

        raise Exception

    # ------------------------------------------------------------------------------------------------------------------
    def _div(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        # Case 1: Other Value is a ScalarValue
        if isinstance(other, ScalarValue):
            new_value.set(self.value / other.value)
            return new_value

        # Case 2: Other Value is an int or float
        if isinstance(other, (int, float)):
            new_value.set(self.value / other)
            return new_value

        raise Exception

    # ------------------------------------------------------------------------------------------------------------------
    def _rsub(self, other):
        new_value = self.copy()
        # Case 1: Other value is also a vector in the same dimension
        if isinstance(other, VectorValue) and other.shape == self.shape:
            new_value.set(other.value - other.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list) and len(other) == self.len:
            new_value.set(np.asarray(other) - self.value)
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(other - self.value)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _copy(self):
        new_value = cp.copy(self)
        new_value.value = np.ndarray(new_value.shape)
        new_value.set(self.value)
        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other)

    def __iadd__(self, other):
        return self.iadd(other)

    def __sub__(self, other):
        return self.sub(other)

    def __isub__(self, other):
        return self.isub(other)

    def __rsub__(self, other):
        return self._rsub(other)

    def __mul__(self, other):
        return self.mul(other)

    def __imul__(self, other):
        return self.imul(other)

    def __rmul__(self, other):
        return self.mul(other)

    def __rmatmul__(self, other):
        return self.mul(other)

    def __itruediv__(self, other):
        return self.idiv(other)

    def __truediv__(self, other):
        return self.div(other)

    def __rtruediv__(self, other):
        raise Exception()

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(value, key)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ == "matmul":
            return self.mul(inputs[0])
        elif ufunc.__name__ == 'subtract':
            raise Exception("Not implemented yet!")
        elif ufunc.__name__ == 'multiply':
            return self.mul(inputs[0])
        elif ufunc.__name__ == 'add':
            raise Exception("Not implemented yet!")
        else:
            raise Exception("Not implemented yet!")

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        out_str = '['
        for i, name in enumerate(self.names):
            out_str = out_str + "{:s}={},".format(name, self.value[i])
        out_str = out_str[:-1] + ']'
        return out_str

    def serialize(self):
        out = {}
        for i, name in enumerate(self.names):
            out[name] = self.value[i]
        return out


# ======================================================================================================================
class MatrixValue(StateValue):
    value: np.ndarray
    shape: tuple

    def __init__(self, name: str = None, shape: tuple = None, value: (list, np.ndarray) = None):
        super().__init__(name)

        if not hasattr(self, 'shape'):
            self.shape = shape

        assert (self.shape is not None and isinstance(self.shape, tuple))

        self.value = np.ndarray(shape=self.shape)
        self.zero()

        if value is not None:
            self.set(value)

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value, index: int = None):
        if index is None:
            if isinstance(value, list):
                new_value = np.asarray(value)
                assert (new_value.shape == self.shape)
                self.value = new_value
            elif isinstance(value, np.ndarray):
                assert (value.shape == self.shape)
                self.value = value
            elif isinstance(value, MatrixValue):
                assert (value.shape == self.shape)
                self.value = value.value
        elif isinstance(index, tuple):
            self.value[index] = value

    # ------------------------------------------------------------------------------------------------------------------
    def zero(self):
        self.set(self._zero())

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, index=None):
        if index is None:
            return self.value
        elif isinstance(index, tuple):
            return self.value[index]

    # ------------------------------------------------------------------------------------------------------------------
    def mul(self, other):
        return self._mul(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def imul(self, other):
        return self._mul(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def add(self, other):
        return self._add(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def iadd(self, other):
        return self._add(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def sub(self, other):
        return self._sub(other, intrinsic=False)

    # ------------------------------------------------------------------------------------------------------------------
    def isub(self, other):
        return self._sub(other, intrinsic=True)

    # ------------------------------------------------------------------------------------------------------------------
    def _zero(self):
        return np.zeros(self.shape)

    # ------------------------------------------------------------------------------------------------------------------
    def _add(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        # Case 1: Other value is also a matrix in the same dimension
        if isinstance(other, MatrixValue) and other.shape == self.shape:
            new_value.set(self.value + other.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list):
            new_value.set(self.value + np.asarray(other))
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(self.value + other)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _sub(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        # Case 1: Other value is also a matrix in the same dimension
        if isinstance(other, MatrixValue) and other.shape == self.shape:
            new_value.set(self.value - other.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list):
            new_value.set(self.value - np.asarray(other))
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(self.value - other)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _rsub(self, other):
        new_value = self.copy()

        # Case 1: Other value is also a matrix in the same dimension
        if isinstance(other, MatrixValue) and other.shape == self.shape:
            new_value.set(other.value - self.value)
            return new_value

        # Case 2: other value is a list
        if isinstance(other, list):
            new_value.set(np.asarray(other) - self.value)
            return new_value

        # Case 3: Other value is a ndarray
        if isinstance(other, np.ndarray) and other.shape == self.shape:
            new_value.set(other - self.value)
            return new_value

        raise Exception()

    # ------------------------------------------------------------------------------------------------------------------
    def _mul(self, other, intrinsic):
        if intrinsic:
            new_value = self
        else:
            new_value = self.copy()

        # Case 1: Other Value is a ScalarValue
        if isinstance(other, ScalarValue):
            new_value.set(self.value * other.value)
            return new_value

        # Case 2: Other is an int or float
        if isinstance(other, (int, float)):
            new_value.set(self.value * other)
            return new_value

        # Case 3: Other is a MatrixValue
        if isinstance(other, MatrixValue):
            new_value.set(self.value @ other.value)
            return new_value

        # Case 4: Other is a np matrix
        if isinstance(other, np.ndarray) and len(other.shape) > 1:
            new_value.set(self.value @ other)
            return new_value

        # Case 5: Other is a VectorValue
        if isinstance(other, VectorValue):
            new_value = other.copy()
            new_value.set(self.value @ other.value)
            return new_value

        # Case 6: Other is a np array
        if isinstance(other, np.ndarray) and len(other.shape) == 1:
            return self.value @ other

        # Case 7
        if isinstance(other, list) and len(other) == self.shape[0]:
            other = np.asarray(other)
            return self.value @ other

        raise Exception

    # ------------------------------------------------------------------------------------------------------------------
    def _rmul(self, other):
        new_value = self.copy()

        # Case 1: Other Value is a ScalarValue
        if isinstance(other, ScalarValue):
            new_value.set(self.value * other.value)
            return new_value

        # Case 2: Other is a scalar value
        if isinstance(other, (int, float)):
            new_value.set(self.value * other)
            return new_value

        # Case 3: Other is a MatrixValue
        if isinstance(other, MatrixValue):
            new_value.set(other.value @ self.value)
            return new_value

        # Case 4: Other is a np matrix
        if isinstance(other, np.ndarray):
            new_value.set(other @ self.value)
            return new_value

        raise Exception

    # ------------------------------------------------------------------------------------------------------------------
    def _copy(self):
        new_value = cp.copy(self)
        new_value.value = np.ndarray(new_value.shape)
        new_value.set(self.value)
        return new_value

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other)

    def __iadd__(self, other):
        return self.iadd(other)

    def __sub__(self, other):
        return self.sub(other)

    def __isub__(self, other):
        return self.isub(other)

    def __rsub__(self, other):
        return self._rsub(other)

    def __mul__(self, other):
        return self.mul(other)

    def __imul__(self, other):
        return self.imul(other)

    def __rmul__(self, other):
        return self.mul(other)

    def __matmul__(self, other):
        return self.mul(other)

    def __rmatmul__(self, other):
        return self.mul(other)

    def __itruediv__(self, other):
        raise Exception

    def __truediv__(self, other):
        raise Exception

    def __rtruediv__(self, other):
        raise Exception()

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(value, key)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ == "matmul":
            return self.mul(inputs[0])
        elif ufunc.__name__ == 'subtract':
            raise Exception("Not implemented yet!")
        elif ufunc.__name__ == 'multiply':
            return self.mul(inputs[0])
        elif ufunc.__name__ == 'add':
            raise Exception("Not implemented yet!")
        else:
            raise Exception("Not implemented yet!")

    def __repr__(self):
        return str(self.value.tolist().__repr__())

    def serialize(self):
        return self.value.tolist()


# ======================================================================================================================
class Dimension:
    base_type: type
    value_type: type
    name: str

    limits: list
    kwargs: dict

    def __init__(self, name: str = None, base_type=None, limits: list = None, **kwargs):
        self.name = name
        self._limits = limits
        if len(kwargs) > 0:
            self.kwargs = kwargs
        else:
            self.kwargs = {}

        if base_type is not None:
            self.base_type = base_type
        self.value_type = type(self.name, (self.base_type,),
                               {**{'name': self.name, 'limits': self.limits}, **self.kwargs})

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, value):
        self._limits = value
        self.value_type = type(self.name, (self.base_type,),
                               {**{'name': self.name, 'limits': self.limits}, **self.kwargs})

    def getValue(self, value=None) -> StateValue:
        val = self.value_type()
        if value is not None:
            val.set(value)
        return val

    def project(self, value):
        return self.getValue(value)


# ======================================================================================================================
class ScalarDimension(Dimension):
    base_type = ScalarValue
    value_type: type

    def __init__(self, name: str = None, base_type=None, **kwargs):
        super().__init__(name, base_type, **kwargs)

    def getValue(self, value=None) -> ScalarValue:
        return super().getValue(value)


# ======================================================================================================================
class VectorDimension(Dimension):
    base_type = VectorValue
    value_type: type

    def __init__(self, name: str = None, base_type=None, **kwargs):
        super().__init__(name, base_type, **kwargs)

    def getValue(self, value=None) -> ScalarValue:
        return super().getValue(value)

    def __iter__(self):
        return iter(self.base_type.names)


# ======================================================================================================================
class MatrixDimension(Dimension):
    base_type = VectorValue
    value_type: type

    def __init__(self, name: str = None, base_type=None, **kwargs):
        super().__init__(name, base_type, **kwargs)

    def getValue(self, value=None) -> ScalarValue:
        return super().getValue(value)


# ======================================================================================================================
class Space:
    dimensions: list[Dimension]
    mappings: list['SpaceMapping']

    parent: 'Space'
    origin: 'State'

    def __init__(self, dimensions: (int, list) = None, parent: 'Space' = None, origin=None):
        if not hasattr(self, 'dimensions'):
            self.dimensions = []

            if isinstance(dimensions, int):
                for i in range(0, dimensions):
                    self.dimensions.append(ScalarDimension(name=f"dim_{i}"))
            elif isinstance(dimensions, list):
                for dim in dimensions:
                    if isinstance(dim, str):
                        self.dimensions.append(ScalarDimension(name=dim))
                    elif isinstance(dim, Dimension):
                        self.dimensions.append(dim)

        if not hasattr(self, 'mappings'):
            self.mappings = []

        self.parent = parent

        if self.parent is not None and origin is None:
            self.origin = self.getState()
        elif self.parent is not None and origin is not None:
            self.origin = self.parent.map(origin)
        else:
            self.origin = None

    # === METHODS ======================================================================================================
    def getState(self, value=None):
        return State(space=self, value=value)

    # ------------------------------------------------------------------------------------------------------------------
    def map(self, value: ('State', list, np.ndarray, int, float)):

        if value is None:
            return None

        # Condition 1: value is of class 'State' and from this space
        if isinstance(value, State) and value.space == self:
            return self.getState(value=value.value)

        # Condition 2: value is of class 'State' from another space
        if isinstance(value, State) and value.space != self:
            # The other space knows a mapping to this space
            if value.space.hasMapping(self):
                mapping = next(mapping for mapping in value.space.mappings if
                               (mapping.space_to == self or isinstance(self, mapping.space_to)))
                return mapping.map(value, self)
            # The value has this state as a parent and is from the same class
            elif type(value.space) == type(self) and value.space.parent == self:
                out = self.getState(value=value.value)
                out = value.space.origin + out
                return out
            elif type(value.space) == type(self):
                out = self.getState(value=value.value)
                return out
            # This space knows a mapping from the other space to this space
            elif self.hasMapping(space_to=self, space_from=value.space):
                mapping = next((mapping for mapping in self.mappings if
                                (mapping.space_to == self or isinstance(self, mapping.space_to)) and (
                                            mapping.space_from == value.space or isinstance(value.space,
                                                                                            mapping.space_from))))
                return mapping.map(value, self)

        # Condition 3: value is a list of the correct length
        if isinstance(value, list) and len(value) == len(self.dimensions):
            return self.getState(value=value)

        # Condition 4: value is a ndarray of the correct length
        if isinstance(value, np.ndarray) and value.shape == (len(self.dimensions),):
            value = value.tolist()
            return self.getState(value=value)

        # Condition 5: State is a numeric value and the space is only 1D:
        if isinstance(value, (int, float)) and len(self.dimensions) == 1:
            return self.getState(value=[value])

        raise Exception("Cannot map the state")

    # ------------------------------------------------------------------------------------------------------------------
    def add(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, False)
        return self._add(value1_map, value2_map, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def iadd(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, True)
        return self._add(value1_map, value2_map, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def sub(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, False)
        return self._sub(value1_map, value2_map, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def isub(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, True)
        return self._sub(value1_map, value2_map, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def mul(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, False)
        return self._mul(value1_map, value2_map, value1, value2, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def imul(self, value1, value2):
        value1_map, value2_map, new_state = self._mapOperators(value1, value2, True)
        return self._mul(value1_map, value2_map, value1, value2, new_state)

    # ------------------------------------------------------------------------------------------------------------------
    def div(self, value1, value2):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def idiv(self, value1, value2):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def concat(self, value1, value2):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def addMapping(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def hasMapping(self, space_to: 'Space', space_from: 'Space' = None):
        if space_from is None:
            return any(
                (mapping.space_to == space_to or isinstance(space_to, mapping.space_to)) for mapping in self.mappings)
        else:
            return any((mapping.space_to == space_to or isinstance(space_to, mapping.space_to) and (
                    mapping.space_from == space_from or isinstance(space_from, mapping.space_from))) for mapping in
                       self.mappings)

    def getDimension(self, index) -> Dimension:
        if isinstance(index, int):
            return self.dimensions[index]
        elif isinstance(index, str):
            dimension = next((dim for dim in self.dimensions if dim.name == index), None)
            return dimension

    def hasDimension(self, name) -> bool:
        return any(dim for dim in self.dimensions if dim.name == name)

    # === PRIVATE METHODS ==============================================================================================
    def _mapOperators(self, value1, value2, intrinsic):
        if intrinsic:
            new_state = value1
        else:
            new_state = self.getState()

        try:
            value1_map = self.map(value1)
        except:
            value1_map = None

        try:
            value2_map = self.map(value2)
        except:
            value2_map = None

        return value1_map, value2_map, new_state

    # ------------------------------------------------------------------------------------------------------------------
    def _mul(self, state1, state2, value1, value2, new_state):

        assert (not (state1 is None and state2 is None))

        # Case 1: value1 is a state with this space or can be mapped into it
        if state1 is not None:

            # Case 1.1: value2 is an int or float
            if isinstance(state2, (int, float)):
                for i, dim in enumerate(self.dimensions):
                    new_state[i] = state1[i] * value2

                return new_state

            # Case 1.2: value2 is a matrix and this space is only consisting of scalar values
            if isinstance(value2, np.ndarray) and value2.shape == (len(self.dimensions), len(self.dimensions)) and all(
                    isinstance(dim, ScalarDimension) for dim in self.dimensions):
                own_value = np.asarray([dim.value for dim in state1.value])

                return value2 @ own_value

            # Case 1.3
            if isinstance(value2, np.ndarray) and len(value2.shape) == 2 and value2.shape[1] == len(
                    self.dimensions) and all(
                isinstance(dim, ScalarDimension) for dim in self.dimensions):
                own_value = np.asarray([dim.value for dim in state1.value])

                return value2 @ own_value

            # Case 1.4: value2 is a MatrixValue and this space is only consisting of scalar values
            if isinstance(value2, MatrixValue) and value2.shape == (len(self.dimensions), len(self.dimensions)) and all(
                    isinstance(dim, ScalarDimension) for dim in self.dimensions):
                raise Exception("TODO: Has to be implemented")  # TODO
        #
        # if value2_map is not None:
        #     ...
        #
        raise Exception("Operation not implemented in this space")

    # ------------------------------------------------------------------------------------------------------------------
    def _add(self, state1, state2, new_state):

        for i, dim in enumerate(self.dimensions):
            new_state[i].set(state1[i] + state2[i])
        return new_state

    # ------------------------------------------------------------------------------------------------------------------
    def _sub(self, state1, state2, new_state):
        for i, dim in enumerate(self.dimensions):
            new_state[i].set(state1[i] - state2[i])
        return new_state

    # ------------------------------------------------------------------------------------------------------------------
    def _div(self, state1, state2, new_state):
        raise Exception("TODO: Has to be implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def _concat(self, state1, state2, new_state):
        raise Exception("TODO: Has to be implemented")

    # === BUILT-IN =====================================================================================================
    def __getitem__(self, item):
        return self.getDimension(item)

    def __repr__(self):
        out_str = '['
        for dim in self.dimensions:
            out_str = out_str + f"{dim.name},"
        out_str = out_str[:-1] + ']'
        return out_str


# ======================================================================================================================
class SpaceMapping:
    space_from: (Space, type) = Space
    space_to: (Space, type) = Space
    mapping: callable

    def __init__(self, space_from: (Space, type) = None, space_to: (Space, type) = None, mapping=None):
        if not (hasattr(self, 'space_from')):
            assert (space_from is not None)
            self.space_from = space_from

        if not (hasattr(self, 'space_to')):
            assert (space_to is not None)
            self.space_to = space_to

        if hasattr(self, '_map'):
            self.mapping = self._map
        else:
            self.mapping = mapping

    # ------------------------------------------------------------------------------------------------------------------
    def map(self, state, space_to: Space = None):

        if state.space == self.space_from or isinstance(state.space, self.space_from):
            # Case 1: the target state is given as instance in this mapping
            if isinstance(self.space_to, Space):
                target_space = self.space_to
            # Case 2: the target state is given as a class and is given as argument here:
            elif isinstance(self.space_to, type) and isinstance(space_to, self.space_to):
                target_space = space_to
            else:
                raise Exception()

            new_state = target_space.getState()
            mapped_state = self.mapping(state)

            if isinstance(mapped_state, dict):
                for key, item in mapped_state.items():
                    new_state[key].set(item)
            else:
                new_state.set(mapped_state)

            # Check for relative state:
            if target_space == state.space.parent:
                new_state = state.space.origin + new_state

            return new_state
        else:
            raise Exception("State cannot be mapped with this mapping")


# ======================================================================================================================
class State:
    space: Space
    value: list[StateValue]

    def __init__(self, space, value=None):
        self.space = space

        # Prepare the value
        self.value = []

        for i, dim in enumerate(self.space.dimensions):
            self.value.append(dim.getValue())

        if value is not None:
            self.set(value)

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value, index: (int, str) = None):
        if index is None:
            if len(self.space.dimensions) > 1:
                if isinstance(value, list):
                    for i in range(0, len(self.space.dimensions)):
                        self.value[i].set(value[i])
                elif isinstance(value, State):
                    for i in range(0, len(self.space.dimensions)):
                        self.value[i].set(value.value[i])
            else:
                self.value[0].set(value)
        elif isinstance(index, int):
            self.value[index].set(value)
        elif isinstance(index, str):
            val = next((val for val in self.value if val.name == index), None)
            val.set(value)

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, index: (int, str) = None):
        if index is None:
            return self.value
        elif isinstance(index, int):
            return self.value[index]
        elif isinstance(index, str):
            val = next((val for val in self.value if val.name == index), None)
            return val

    # ------------------------------------------------------------------------------------------------------------------
    def map(self, space: Space):
        return space.map(value=self)

    # ------------------------------------------------------------------------------------------------------------------
    def serialize(self):
        out = {}
        for val in self.value:
            out[val.name] = val.serialize()
        return out

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return self.space.add(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        return self.space.sub(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other):
        return self.space.mul(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __rmul__(self, other):
        return self.space.mul(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __matmul__(self, other):
        return self.space.mul(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __rmatmul__(self, other):
        return self.space.mul(self, other)

    # ------------------------------------------------------------------------------------------------------------------
    def __imatmul__(self, other):
        raise Exception("TODO: Needs to be implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def __truediv__(self, other):
        raise Exception("TODO: Needs to be implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def __itruediv__(self, other):
        raise Exception("TODO: Needs to be implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def __rshift__(self, other):
        raise Exception("TODO: Needs to be implemented")

    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, item):
        return self.get(item)

    # ------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, key, value):
        self.set(value, key)

    # ------------------------------------------------------------------------------------------------------------------
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc.__name__ == "matmul":
            return self.__mul__(inputs[0])
        elif ufunc.__name__ == 'subtract':
            raise Exception("Not implemented yet!")
            # raise Exception("Not implemented yet!")
        elif ufunc.__name__ == 'multiply':
            raise Exception("Not implemented yet!")
            # return self.mul(inputs[0])
        elif ufunc.__name__ == 'add':
            raise Exception("Not implemented yet!")
        else:
            raise Exception("Not implemented yet!")

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        out = '['
        for i, dim in enumerate(self.space.dimensions):
            out = out + f"{dim.name}={self.value[i]},"
        out = out[:-1] + ']'
        return out


# ======================================================================================================================
# SPECIAL SPACES

class PositionVector3D(VectorValue):
    names = ['x', 'y', 'z']
    shape = (3,)
    name = 'pos'

    def __init__(self, name: str = None, value: (list, np.ndarray) = None, limits: list = None,
                 discretization: list = None, wrapping: (list, bool) = True):
        super().__init__(name=name, value=value, limits=limits, discretization=discretization, wrapping=wrapping)


# ======================================================================================================================
class PositionVector2D(VectorValue):
    names = ['x', 'y']
    shape = (2,)
    name = 'pos'

    def __init__(self, name: str = None, value: (list, np.ndarray) = None, limits: list = None,
                 discretization: list = None, wrapping: (list, bool) = True):
        super().__init__(name=name, value=value, limits=limits, discretization=discretization, wrapping=wrapping)


# ======================================================================================================================
class OrientationMatrix3D(MatrixValue):
    shape = (3, 3)
    name = 'ori'

    def __init__(self, name: str = None, value: (list, np.ndarray) = None):
        super().__init__(name, value)

    def getHeading(self):
        return orientation_utils.psiFromRotMat(self.value)

    def setFromEuler(self, angles, convention):
        q = qmt.quatFromEulerAngles(angles=np.asarray(angles), axes=convention, intrinsic=True)
        self.set(qmt.quatToRotMat(q))

    def random(self):
        q = qmt.randomQuat()
        self.set(qmt.quatToRotMat(q))

    def _zero(self):
        return np.eye(self.shape[0])

    def _add(self, other, intrinsic):
        ...


# ======================================================================================================================
class Space3D(Space):
    dimensions = [VectorDimension(name='pos', base_type=PositionVector3D),
                  MatrixDimension(name='ori', base_type=OrientationMatrix3D)]

    def _add(self, state1, state2, new_state):
        add_value = state1['ori'].value @ state2['pos']
        new_state['pos'] = state1['pos'] + add_value
        new_state['ori'] = state1['ori'] @ state2['ori']
        return new_state

    def _mul(self, state1, state2, value1, value2, new_state):
        raise Exception("Multiplication is not allowed in this space")

    def translate(self):
        raise Exception("Not yet implemented")

    def rotate(self):
        raise Exception("Not yet implemented")


# ======================================================================================================================
class Space2D(Space):
    dimensions = [VectorDimension(name='pos', base_type=PositionVector2D),
                  ScalarDimension(name='psi', limits=[0, 2 * pi], wrapping=True)]

    def _add(self, state1, state2, new_state):
        add_value = orientation_utils.rotmatFromPsi_2D(state1['psi'].value) @ state2['pos']
        new_state['pos'] = state1['pos'] + add_value
        new_state['psi'] = state1['psi'] + state2['psi']
        return new_state

    def _mul(self, state1, state2, value1, value2, new_state):
        raise Exception("Multiplication is not allowed in this space")


# ======================================================================================================================
class CoordSpace2D(Space):
    dimensions = [ScalarDimension(name='x'), ScalarDimension(name='y')]


# ======================================================================================================================
class CoordSpace1D(Space):
    dimensions = [ScalarDimension(name='x')]


# ======================================================================================================================
class Mapping_Coord1Dto2D(SpaceMapping):
    space_to = CoordSpace2D
    space_from = CoordSpace1D

    def _map(self, state):
        out = {
            'x': state['x'],
            'y': 0
        }
        return out


# ======================================================================================================================
class Mapping2D2D(SpaceMapping):
    space_to = Space2D
    space_from = Space2D

    def __init__(self, offset_z=None):
        super().__init__()

        if offset_z is not None:
            self.offset_z = offset_z

    def _map(self, state_2d):
        out = {
            'pos': state_2d['pos'].value,
            'psi': state_2d['psi']
        }
        return out


class Mapping3D3D(SpaceMapping):
    space_to = Space3D
    space_from = Space3D

    def __init__(self):
        super().__init__()

    def _map(self, state_3d):
        out = {
            'pos': state_3d['pos'],
            'ori': state_3d['ori']
        }
        return out


class Mapping2D3D(SpaceMapping):
    offset_z = 0
    space_to = Space3D
    space_from = Space2D

    def __init__(self, offset_z=None):
        super().__init__()

        if offset_z is not None:
            self.offset_z = offset_z

    def _map(self, state_2d):
        out = {
            'pos': [state_2d['pos']['x'], state_2d['pos']['y'], self.offset_z],
            'ori': orientation_utils.rotmatFromPsi(state_2d['psi'].value)
        }
        return out


class Mapping3D2D(SpaceMapping):
    offset_z = 0
    space_to = Space2D
    space_from = Space3D

    def __init__(self, offset_z=None):
        super().__init__()

        if offset_z is not None:
            self.offset_z = offset_z

    def _map(self, state_3d):
        out = {
            'pos': [state_3d['pos']['x'], state_3d['pos']['y']],
            'psi': orientation_utils.psiFromRotMat(state_3d['ori'].value)
        }
        return out


Space2D.mappings = [Mapping2D3D(), Mapping2D2D()]
Space3D.mappings = [Mapping3D2D(), Mapping3D3D()]
CoordSpace1D.mappings = [Mapping_Coord1Dto2D()]
