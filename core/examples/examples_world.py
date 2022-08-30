from scioi_py_core.core import world as world


def example_1():
    # First define the spaces:
    configuration_space = world.spaces.Space(['x', 'y', 'theta'])
    coordinate_space = world.spaces.Space(['x', 'y'])
    mapping = world.spaces.Mapping(space_from=configuration_space, space_to=coordinate_space,
                                   mapping=lambda config: [config['x'], config['y']])

    spaces = world.WorldSpaces()
    spaces.configuration_space = configuration_space
    spaces.coordinate_space = coordinate_space
    spaces.map_configToCoordinateSpace = mapping

    # Initialize a world with the given spaces
    w = world.World(spaces=spaces)

    # Define an object
    obj = world.WorldObject(name='Object 1', world=w)

    obj.configuration = [1, 2, 0]

    print(obj.coordinate)

    # Get Objects by name
    o2 = w.getObjectsByName('Object 1')

    # Get Objects by type
    o3 = w.getObjectsByType(world.WorldObject)

    w.removeObject(obj)

    pass


if __name__ == '__main__':
    example_1()
