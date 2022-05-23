import ctypes
import threading
import time
from typing import List, Dict, Tuple, Set, Optional, Union, Sequence, Callable, Iterable, Iterator


# =======================================================================================================
# source code from SO
# https://stackoverflow.com/questions/19749404/is-it-possible-to-rumble-a-xbox-360-controller-with-python

# Define necessary structures
class XInputVibration(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]


# Load XInput.dll (-> change version number if needed (C:\Windows\System32\XInput1_<version number>))
# Or download the .dll file from the internet, its the MICROSOFT COMMON CONTROLLER API
# 22.07.2021: newest version == 4
XInput = ctypes.windll.xinput1_4

# Set up function argument types and return type
XInputSetState = XInput.XInputSetState
XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XInputVibration)]
XInputSetState.restype = ctypes.c_uint


# Create a helper function like this:
def set_vibration(controller, left_motor, right_motor):
    vibration = XInputVibration(int(left_motor * 65535), int(right_motor * 65535))
    XInputSetState(controller, ctypes.byref(vibration))


# =======================================================================================================
# favorites

def strong_rumble():
    set_vibration(0, 0.4, 0.4)
    time.sleep(0.25)
    set_vibration(0, 0, 0)


def weak_rumble():
    set_vibration(0, 0.4, 0.4)
    time.sleep(0.15)
    set_vibration(0, 0, 0)


# =======================================================================================================


class RumbleHandlerThread(threading.Thread):
    enable_flags: Dict[str, bool]
    rumble_configs: Dict[str, List[float]]
    joystick_instance_id: int

    def __init__(self) -> None:
        super().__init__()
        self.enable_flags = {"weak": False,
                             "strong": False}
        self.rumble_configs = {"weak": [0.4, 0.4, 0.15],
                               "strong": [0.4, 0.4, 0.25]}
        self.joystick_instance_id = -1

    def run(self):
        while True:
            time.sleep(0.01)
            for key, enable in self.enable_flags.items():
                if enable:
                    left, right, dur = self.rumble_configs[key]
                    self.rumble(self.joystick_instance_id, left, right, dur)
                    self.enable_flags[key] = False

    @staticmethod
    def rumble(controller: int, left_motor: float, right_motor: float, duration: float) -> None:
        set_vibration(controller, left_motor, right_motor)
        time.sleep(duration)
        set_vibration(controller, 0, 0)

    def request_rumble(self, joystick_instance_id: int, rumble_type: str = "weak") -> None:
        self.joystick_instance_id = joystick_instance_id
        if rumble_type not in self.enable_flags.keys():
            rumble_type = "weak"
        self.enable_flags[rumble_type] = True