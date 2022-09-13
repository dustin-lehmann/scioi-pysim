""" Example docstring """
import numpy as np
import scipy.io

import p11_simpy.core.simulation as simulation
from p11_simpy.visualization.core.D3.babylon.babylon import BABYLON_LiveBackend

# Sample time as used in the data. This sample time will be used to update the simulation
Ts = 0.02

# Start an empty simulator in real-time mode
sim = simulation.Simulator(mode='rt', Ts=Ts, objects=[])

# Load the corresponding backend
webapp = BABYLON_LiveBackend("./example_twipr_obstacle.html", options={'agents': 1})


def received_message(*args, **kwargs):
    print("MESSAGE!")


webapp.webapp.on('message', received_message)

# Load the recorded data that is going to be played
data = scipy.io.loadmat('./obstacle1optimalTimeViaTime0Resampled.mat')
time = data['time']
states = data['states']
i = 0

# The initial wait is for the webapp to load and all objects to be rendered
initial_wait = 5
time = np.vstack((np.zeros((int(initial_wait / Ts), 1)), time))
states = np.vstack((np.zeros((int(initial_wait / Ts), 4)), states))


def user_output(*args, **kwargs):
    """ This function will be called at the end of each simulation step"""
    global i, time, states
    if i < len(time):
        sample = {
            't': sim.t,
            '1': {'t': time[i], 'x': states[i, 0] * 1000 - 1000, 'y': 0, 'theta': states[i, 2],
                  'psi': 0},
        }
        webapp.sendSample(sample)
    i = i + 1


def user_sim_exit(*args, **kwargs):
    """ This function will be called after the simulation has ended"""
    pass


# Hook the output function into the simulation
sim.user_output = user_output

# Initialize the simulation
sim.init()

# Run the simulation in a separate thread
sim.run(time=20, thread=True)

# Start the Webapp
webapp.start()
