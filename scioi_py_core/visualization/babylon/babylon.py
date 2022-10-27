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
    Ts = 0.04

    # === INIT =========================================================================================================
    def __init__(self, webapp: str = babylon_path + '/pysim_env.html', webapp_config=None,
                 world_config=None, object_config=babylon_path + 'object_config.json'):

        self._config = {
            'world': {},
            'object_config': {},
            'general': {}
        }

        # Load the object configuration, which stores the information which Babylon Object needs to be created for a
        # certain class

        if isinstance(object_config, str):
            with open(object_config) as f:
                object_config = json.load(f)

        assert (isinstance(object_config, dict))

        self._config['object_config'] = object_config

        if webapp is not None:
            self.webapp_path = webapp

        assert (hasattr(self, 'webapp_path') and self.webapp_path is not None)

        self._last_sample = {}
        self._run = False
        self._data_queue = queue.Queue()
        self._webapp = None
        self._thread = threading.Thread(target=self._threadFunction, daemon=True)
        self._thread.start()

    # ==================================================================================================================
    class Process(qmt.Block):
        last_sample: dict
        q: queue.Queue

        def __init__(self, q: queue.Queue):
            super().__init__()
            self.last_sample = {}
            self.q = q

        def step(self, input):
            if not self.q.empty():
                sample = self.q.get()
                self.last_sample = sample
                return sample
            else:
                return self.last_sample

    # === METHODS ======================================================================================================
    def start(self):
        logging.info("Starting Babylon visualization")
        while self._webapp is None:
            ...
        self._webapp.run()

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
        # asyncio.set_event_loop(asyncio.new_event_loop())

        self._webapp = qmt.Webapp(self.webapp_path, config=self._config, show='chromium')
        self._webapp.setupOnlineLoop(qmt.ClockDataSource(self.Ts), self.Process(self._data_queue))

        while True:
            time.sleep(1)
