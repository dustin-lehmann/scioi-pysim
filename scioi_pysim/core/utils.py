from dataclasses import dataclass
from functools import reduce
import random
import math


def dict_to_dataclass(dictionary: dict, data: dataclass):
    if dict is None:
        return
    for key, value in dictionary.items():
        if hasattr(data, key):
            setattr(data, key, value)


def xor(*args):
    return sum(list(args)) == 1


def wrap(interval, value):
    def wrapMax(value, max):
        return math.fmod(max + math.fmod(value, max), max)

    return interval[0] + wrapMax(value - interval[0], interval[1] - interval[0])


class NoneGenerator:

    def __init__(self):
        pass

    def __getitem__(self, item):
        return None


class NoDefaultProvided(object):
    pass


def getattrd(obj, name, default=1):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    https://stackoverflow.com/questions/11975781
    """

    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError as e:
        if default != NoDefaultProvided:
            return default


def hasattrd(obj, name):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    https://stackoverflow.com/questions/11975781
    """

    try:
        reduce(getattr, name.split("."), obj)
        return True
    except AttributeError as e:
        return False


def set_list(list, key, value):
    while not (key < len(list)):
        list.append(None)
    list[key] = value


def testfun():
    print("Hallo")


def decision(probability):
    return random.random() < probability


def xtick_labels_hide(axis, multiplicator):
    # labels = axis.get_xticklabels()
    labels = axis.get_xticks().tolist()
    new_labels = [str(item) for item in labels]
    for i, label in enumerate(labels):
        if label % multiplicator != 0:
            new_labels[i] = ''
        axis.set_xticklabels(new_labels)
