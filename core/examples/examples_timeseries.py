import numpy as np

import scioi_py_core.core.timeseries as timeseries
import scioi_py_core.core.spaces as spaces


def example_1():
    # Define a simple vector
    vec = np.arange(0, 100, 1)

    # Transform the vector into a timeseries object
    ts = timeseries.Timeseries(data=vec)

    # Plot the timeseries
    ts.plot(title='Example 1 Timeseries')


def example_2():
    # Generate a default timeseries
    ts = timeseries.Timeseries(default=0, length=100, Ts=0.1)

    # Set individual values
    ts[20] = 1
    ts[21:35] = -1

    # Plot the default timeseries
    ts.plot(title='Example 2 Timeseries')


def example_3():
    # Get a time vector:
    t = np.arange(0, 10, 0.1)

    # Generate two vectors of data
    vec1 = np.sin(t)
    vec2 = np.cos(t)

    # Define a state space
    space = spaces.Space(['v', 'a'])

    # Map the two vectors into spaces
    state_vec = []
    for i in range(0, len(vec1)):
        state_vec.append(space.map([vec1[i], vec2[i]]))

    # Put the data into timeseries
    ts = timeseries.Timeseries(state_vec, Ts=0.1)
    ts.plot(legend=space.dimension_names)

    # Extract one state from the timeseries
    v = ts['v']

    # Plot this one state
    v.plot(title='v plot', legend='v')


if __name__ == '__main__':
    example_1()
    # example_2()
    # example_3()
