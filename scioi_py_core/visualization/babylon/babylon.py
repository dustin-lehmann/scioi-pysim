import asyncio
import json
import logging
import os
import threading
import time

import qmt
import queue
import sys

# ======================================================================================================================
babylon_path = f"{os.path.dirname(__file__)}/babylon_lib/"


# ======================================================================================================================
class BabylonVisualization:
    webapp_path: str

    _webapp: qmt.Webapp
    _data_queue: queue.Queue
    _thread: threading.Thread
    _last_sample: dict

    _config: dict
    _run: bool
    Ts = 0.04  # 0.04

    # === INIT =========================================================================================================
    def __init__(self, webapp: str = babylon_path + '/pysim_env.html', webapp_config=None,
                 world_config=None, object_config=babylon_path + 'object_config.json', fetch_function: callable = None):

        self._config = {
            'world': {},
            'object_config': {},
            'webapp_config': {}
        }

        # Load the object configuration, which stores the information which Babylon Object needs to be created for a
        # certain class
        if isinstance(object_config, str):
            with open(object_config) as f:
                object_config = json.load(f)

        assert (isinstance(object_config, dict))
        self._config['object_config'] = object_config

        # World config: Describes the world and all the objects within the world
        self._config['world'] = world_config

        # General config
        self._config['webapp_config'] = webapp_config

        # -----
        if webapp is not None:
            self.webapp_path = webapp

        assert (hasattr(self, 'webapp_path') and self.webapp_path is not None)

        self._last_sample = {}
        self._run = False
        self._data_queue = queue.Queue()
        self._webapp = None

        self.fetch_function = fetch_function

    # ==================================================================================================================
    class Process(qmt.Block):
        last_sample: dict
        q: queue.Queue
        fetch_function: callable

        def __init__(self, q: queue.Queue, fetch_function: callable = None):
            super().__init__()
            self.last_sample = {}
            self.q = q
            self.fetch_function = fetch_function

        def step(self, input):
            if not self.q.empty():
                sample = self.q.get()
                self.last_sample = sample
                return sample
            else:
                if not self.fetch_function is None:
                    sample = self.fetch_function()
                    self.last_sample = sample
                    return sample
                else:
                    return self.last_sample

    # === METHODS ======================================================================================================
    def setWorldConfig(self, world_config):
        self._config['world'] = world_config

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        logging.info("Starting Babylon visualization")
        self._thread = threading.Thread(target=self._threadFunction, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def sendSample(self, sample, force=False):
        if not force:
            if self._data_queue.empty():
                self._data_queue.put(sample)
        else:
            with self._data_queue.mutex:
                self._data_queue.queue.clear()
            self._data_queue.put(sample)

    # === PRIVATE METHODS ==============================================================================================
    def _threadFunction(self):

        # Define a new event loop, otherwise it's not working
        asyncio.set_event_loop(asyncio.new_event_loop())
        self._webapp = qmt.Webapp(self.webapp_path, config=self._config, show='chromium')
        self._webapp.setupOnlineLoop(qmt.ClockDataSource(self.Ts), self.Process(self._data_queue, self.fetch_function))
        self._webapp.run()
        # self._webapp.runInProcess()
        while True:
            time.sleep(1)
