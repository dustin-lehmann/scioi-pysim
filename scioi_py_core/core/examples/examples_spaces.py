from scioi_py_core.core import spaces as spaces


def example_1():
    print("Example 1: Simple State Spaces")
    # Define a state-space by just naming the dimensions
    space = spaces.Space(['x', 'y', 'z'])

    # Get a zero state from the space
    state = space.zero()

    # Set the x-component of the state
    state['x'] = 3

    # Print the x-component by position
    print(state[0])

    # Print the x-component by name
    print(state['x'])


def example_2():
    print("Example 2: Complex State Spaces")
    # Build more complex dimensions
    x_dimension = spaces.Dimension(name='x', discretization=0, limits=[-2, 2], wrapping=True)
    y_dimension = spaces.Dimension(name='y', discretization=0.5)
    z_dimension = spaces.Dimension(name='z', discretization=0, limits=[-2, 2], wrapping=False)

    # Initialize the state space
    space = spaces.Space(dimensions=[x_dimension, y_dimension, z_dimension])

    # Map an array into the state-space
    state = space.map([3, 1.6, -4])

    # Print the state and see the behavior of the different dimension settings
    print(state)


def example_3():
    print("Example 3: States")

    # Define a state space
    space = spaces.Space(['x', 'y', 'z'])

    # Get two states
    state1 = space.map([1, 2, 3])
    state2 = space.map([4, 5, 6])

    # Add and subtract the two states
    state3 = state1 + state2
    print(state3['x'])

    state4 = state1 - state2
    print(type(state4))


def example_4():
    print("Example 4: Mappings between Spaces")

    # Define a state space with 3 coordinates
    space1 = spaces.Space(['x', 'y', 'z'])

    # Define a second space with 2 coordinates p and q
    space2 = spaces.Space(['p', 'q'])

    # Define a mapping from space1 to space2
    space_map = spaces.Mapping(space_from=space1, space_to=space2,
                               mapping=lambda state: [2 * state['x'], 0.5 * state['y']],
                               inverse=None)

    # Get a state from space1 and map it to space2
    state1_1 = space1.map([1, 2, 3])
    print(state1_1)
    state1_2 = space2.map(state1_1)
    print(state1_2)

    # Since there is no inverse mapping the following will fail:
    try:
        state1_2_inverse = space1.map(state1_2)
    except TypeError:
        print("No inverse mapping defined")

    # Define an inverse mapping. Since there was some information loss from space1 to space2, we have to set a
    # dimension constant
    space_map.inverse = lambda state: [0.5 * state['p'], 2 * state['q'], 0]

    state1_2_inverse = space1.map(state1_2)
    print(state1_2_inverse)


if __name__ == '__main__':
    example_1()
    example_2()
    example_3()
    example_4()
