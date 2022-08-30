import numpy as np
from typing import ClassVar
import copy as cp
import matplotlib.pyplot as plt


from .spaces import State


# Timeseries ###########################################################################################################
class Timeseries:
    data: list
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
    def plot(self, title=None, hold=False, log=False, legend=None, **kwargs):
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
        if legend is not None:
            plt.legend(legend)
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
        elif isinstance(key, str) and self.type == State:
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