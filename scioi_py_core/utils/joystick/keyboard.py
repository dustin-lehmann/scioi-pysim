import threading
import time

from pynput.keyboard import Key, Listener, Controller



class ArrowKeys:

    _thread: threading.Thread
    keys: dict

    def __init__(self):

        self.keys = {
            'UP': 0,
            'DOWN': 0,
            'LEFT': 0,
            'RIGHT': 0,
        }

        self._exit = False
        self._thread = threading.Thread(target=self._threadFunction, daemon=True)
        self.start()

    def start(self):
        self._exit = False
        self._thread.start()

    def exit(self):
        self._exit = True

    def _threadFunction(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if Key.up == key:
            self.keys['UP'] = 1
        if Key.down == key:
            self.keys['DOWN'] = 1
        if Key.left == key:
            self.keys['LEFT'] = 1
        if Key.right == key:
            self.keys['RIGHT'] = 1

    def on_release(self, key):
        if Key.up == key:
            self.keys['UP'] = 0
        if Key.down == key:
            self.keys['DOWN'] = 0
        if Key.left == key:
            self.keys['LEFT'] = 0
        if Key.right == key:
            self.keys['RIGHT'] = 0





