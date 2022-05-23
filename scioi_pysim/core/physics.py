import scioi_pysim.core as core


class PhysObject:
    configuration_space: core.spaces.StateSpace
    configuration: core.spaces.State

    object_config: dict

    def __init__(self, configuration_space: core.spaces.StateSpace = None, configuration: core.spaces.State = None,
                 object_config: dict = None):
        assert (configuration_space is not None)
        self.configuration_space = configuration_space

        if configuration is None:
            self.configuration = self.configuration_space.zeros()
        else:
            self.configuration = configuration

        self.object_config = object_config

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._configuration = self.configuration_space.map(value)

    def update(self, configuration: core.spaces.State):
        self.configuration = configuration

    def check_collision(self, object):
        pass

    def inner_point(self, point):
        pass

    def _collision(self):
        pass


class Point2D(PhysObject):
    """
        object_config:
        - anchor: anchor configuration relative to the center of the circle
        """

    def __init__(self, configuration_space: core.spaces.StateSpace = None, configuration: core.spaces.State = None,
                 object_config: dict = None):
        super().__init__(configuration_space, configuration, None)

        default_config = {'anchor': self.configuration_space.zeros()}

        self.object_config = {**default_config, **object_config}


class Circle2D(PhysObject):
    """
    object_config:
    - diameter: Diameter of the circle
    - anchor: anchor configuration relative to the center of the circle
    """

    def __init__(self, configuration_space: core.spaces.StateSpace = None, configuration: core.spaces.State = None,
                 object_config: dict = None):
        super().__init__(configuration_space, configuration, None)

        default_config = {'diameter': 0,
                          'anchor': self.configuration_space.zeros()}

        self.object_config = {**default_config, **object_config}


class Rectangle2D(PhysObject):
    """
    object_config:
    - a,b: Side lengths of the rectangle
    - anchor: anchor configuration relative to the center of the rectangle
    """

    def __init__(self, configuration_space: core.spaces.StateSpace = None, configuration: core.spaces.State = None,
                 object_config: dict = None):
        super().__init__(configuration_space, configuration, None)

        default_config = {'a': 0,
                          'b': 0,
                          'anchor': self.configuration_space.zeros()}

        self.object_config = {**default_config, **object_config}
