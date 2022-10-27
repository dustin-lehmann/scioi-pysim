import qmt
import queue


class Process(qmt.Block):
    last_sample: dict
    q: queue.Queue

    def __init__(self, q: queue.Queue):
        self.last_sample = {}
        self.q = q

    def step(self, input):
        if not self.q.empty():
            sample = self.q.get()
            self.last_sample = sample
            return sample
        else:
            return self.last_sample


class BABYLON_LiveBackend:
    last_sample: dict
    webapp: qmt.Webapp
    data_queue: queue.Queue

    def __init__(self, webapp_url, options=None):
        if options is None:
            options = {}

        self.last_sample = {}
        self.webapp = qmt.Webapp(webapp_url, config=options, show='chromium')
        self.data_queue = queue.Queue()
        self.webapp.setupOnlineLoop(qmt.ClockDataSource(0.04), Process(self.data_queue))

    def start(self):
        self.webapp.run()

    def sendSample(self, sample, force=False):
        if not force:
            if self.data_queue.empty():
                self.data_queue.put(sample)
        else:
            with self.data_queue.mutex:
                self.data_queue.queue.clear()
            self.data_queue.put(sample)
