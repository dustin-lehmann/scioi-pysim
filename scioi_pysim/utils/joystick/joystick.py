from typing import List, Dict, Tuple, Set, Optional, Union, Sequence, Callable, Iterable, Iterator
import threading
import pygame
import time

# My Imports
from .rumble import RumbleHandlerThread, weak_rumble, strong_rumble


def sign(x):
    return x and (1, -1)[x < 0]


class Joystick:
    joystick: pygame.joystick.Joystick
    information: Dict[str, Union[int, str]]
    mapping: Dict[str, int]
    dead_band: float
    id: int
    connected: bool
    exit: bool
    axes: list
    callbacks: list

    def __init__(self, Ts: float = 0.04) -> None:
        self.connected = False
        self.exit = False
        self.axes = [0, 0, 0, 0, 0, 0]
        self.Ts = Ts
        self.callbacks = []

        thread = threading.Thread(target=self.thread)
        thread.start()

    def thread(self):
        pygame.init()
        pygame.joystick.init()
        while not self.exit:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                self.joystick = pygame.joystick.Joystick(0)
                self.id = self.joystick.get_instance_id()
                self.connected = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.instance_id == 0:
                    callback = next((x for x in self.callbacks if x.type == 'button' and x.id == event.button), None)
                    if callback is not None:
                        callback()
            elif event.type == pygame.JOYHATMOTION:
                if event.instance_id == 0:
                    callback = next((x for x in self.callbacks if x.type == 'hat'), None)
                    if callback is not None:
                        callback(value=event.value)
            elif event.type == pygame.JOYAXISMOTION:
                if event.instance_id == 0:
                    callback = next((x for x in self.callbacks if x.type == 'axis' and x.id == event.axis), None)
                    if callback is not None:
                        callback(value=event.value)

        joystick_count = pygame.joystick.get_count()

        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            if joystick == self.joystick:
                axes = joystick.get_numaxes()

                for j in range(axes):
                    self.axes[j] = joystick.get_axis(j)
        time.sleep(self.Ts)

    def set_callback(self, type, id, callback, *args, **kwargs):

        self.callbacks.append(JoystickButtonCallback(type, id, callback, args, kwargs))


class JoystickButtonCallback:
    def __init__(self, type, button, function, args, kwargs):
        self.type = type
        self.id = button
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)
