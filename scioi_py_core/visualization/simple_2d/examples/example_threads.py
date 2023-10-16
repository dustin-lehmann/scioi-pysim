import matplotlib
matplotlib.use("qtagg")
import matplotlib.pyplot as plt
import threading
import time

from PySide2 import QtCore

class Call_in_QT_main_loop(QtCore.QObject):
    signal = QtCore.Signal()

    def __init__(self, func):
        super().__init__()
        self.func = func
        self.args = list()
        self.kwargs = dict()
        self.signal.connect(self._target)

    def _target(self):
        self.func(*self.args, **self.kwargs)

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.signal.emit()

@Call_in_QT_main_loop
def plot_a_graph():
    f,a = plt.subplots(1)
    line = plt.plot(range(10))
    print("plotted graph")
    plt.show()
    print("plotted graph")
    print(threading.current_thread())  # print the thread that runs this code

def worker():
    print("fhdjsf")
    plot_a_graph()
    print(threading.current_thread())  # print the thread that runs this code
    time.sleep(4)

testthread = threading.Thread(target=worker)

testthread.start()