import dataclasses
import logging
import re
from abc import ABC, abstractmethod
from typing import Union

import scioi_py_core.core.spaces as core_spaces
import scioi_py_core.core.scheduling as scheduling
import scioi_py_core.core.physics as physics


# ======================================================================================================================
@dataclasses.dataclass
class WorldSpaces:
    coordinate_space: core_spaces.Space = None
    configuration_space: core_spaces.Space = None
    coordinate_mapping: core_spaces.Mapping = None


@dataclasses.dataclass
class CollisionSettings:
    check: bool = False
    collidable: bool = True
    includes: ['WorldObject'] = dataclasses.field(default_factory=lambda: [WorldObject])
    excludes: ['WorldObject'] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class CollisionData:
    settings: CollisionSettings = dataclasses.field(default_factory=CollisionSettings)
    collision_state: bool = False
    collision_objects: list = dataclasses.field(default_factory=list)


# ======================================================================================================================
class WorldObject(scheduling.ScheduledObject):
    world: 'World'
    parent: 'WorldObject'

    spaces: WorldSpaces

    physics: physics.PhysicalBody
    collision: CollisionData
    coordinate: core_spaces.State
    configuration: core_spaces.State

    name: str  # Name given by the user
    id: str  # Unique ID of the object in the corresponding world
    object_type: str = 'object'

    # === INIT =========================================================================================================
    def __init__(self, name: str = None, world: 'World' = None, parent: 'WorldObject' = None,
                 spaces: WorldSpaces = None, *args, **kwargs):

        self._configuration = None
        self.id = f"{type(self)}_{id(self)}"
        super().__init__()

        if not (name is None and hasattr(self, 'name')):
            self.name = name

        self.spaces = spaces
        self.world = world
        self.parent = parent

        self.collision = CollisionData()

        scheduling.Action(name='physics_update', function=self.action_physics_update,
                          lambdas={'config': lambda: self.configuration}, object=self)

        if self.world is not None:
            if hasattr(world, 'addObject'):
                world.addObject(self)

        if self.parent is not None:
            if hasattr(self.parent, 'addChildObject'):
                self.parent.addChildObject(self)

        if self.spaces is not None:
            self.configuration = self.spaces.configuration_space.none()

    # === PROPERTIES ===================================================================================================

    @property
    def coordinate(self):
        return self.spaces.coordinate_space.map(self.configuration)

    @coordinate.setter
    def coordinate(self, value):
        raise Exception("Setting coordinate is not implemented yet. Set the configuration instead.")

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        if value is not None and self.spaces is not None:
            value = self.spaces.configuration_space.map(value)
            self._configuration = value
            # if self.world is not None:
            #     value = self.world.spaces.configuration_space.map(value)
            #     self._configuration = value
            # elif self.parent is not None:
            #     value = self.parent.spaces.configuration_space.map(value)
            #     self._configuration = value

    @property
    def parameters(self):
        return self._getParameters()

    # === METHODS ======================================================================================================
    def getSample(self):
        sample = {'name': self.name,
                  'class': self.__class__.__name__,
                  'object_type': self.object_type,
                  'configuration': self.configuration,
                  'parameters': self.parameters
                  }
        return sample

    # ------------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def _getParameters(self):
        """
        this function is supposed to be tailored to each different class type since the can have specific parameters
        relevant for babylon
        :return: specific object parameters
        """
        params = {}
        return params

    def _getAbsoluteConfiguration(self):
        ...

    # === ACTIONS ======================================================================================================
    @abstractmethod
    def action_physics_update(self, config, *args, **kwargs):
        pass

    def _init(self):
        pass


# ======================================================================================================================
class WorldObjectGroup(WorldObject, ABC):
    objects: dict

    def addChildObject(self, obj: 'WorldObject'):
        obj.scheduling.parent = self
        obj.parent = self

        # Check if the object has their own spaces. If so, there needs to be a mapping to the worlds spaces
        if hasattr(obj, 'spaces'):
            assert (self.spaces.configuration_space.has_mapping(obj.spaces.configuration_space))
            assert (self.spaces.coordinate_space.has_mapping(obj.spaces.coordinate_space))
        else:
            obj.spaces = self.spaces

        if not (hasattr(obj, 'configuration')) or obj.configuration is None:
            obj.configuration = obj.spaces.configuration_space.none()

        self.objects[obj.id] = obj

        # Add all the child actions to own actions
        for name, action in self.scheduling.actions.items():
            if name in obj.scheduling.actions and not name.startswith("_"):
                obj.scheduling.actions[name].parent = action


class RelativeConfigurationSpace(core_spaces.Space):
    parent: WorldObject


# ======================================================================================================================
class World(scheduling.ScheduledObject):
    spaces: WorldSpaces
    objects: dict[str, 'WorldObject']
    name = 'world'
    size: None  # Add the World Dimensions here and not in the Spaces. This makes it much easier

    # === INIT =========================================================================================================
    def __init__(self, spaces: WorldSpaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spaces = spaces
        self.objects: dict[str, 'WorldObject'] = {}

    # === METHODS ======================================================================================================
    def addObject(self, objects: Union[WorldObject, dict]):

        if not (isinstance(objects, list)):
            objects = [objects]

        for obj in objects:
            assert (isinstance(obj, WorldObject))

            # Check if the object already exists in  the list of objects. If so, just raise a warning and continue
            if obj in self.objects.values():
                logging.warning("Object already exists in world")
                continue

            for _, other in self.objects.items():
                if obj.name == other.name:
                    logging.warning(f"There already exists an object with name \"{obj.name}\".")
                    break

            obj.scheduling.parent = self
            obj.world = self

            # Check if the object has their own spaces. If so, there needs to be a mapping to the worlds spaces
            if hasattr(obj, 'spaces'):
                assert (self.spaces.configuration_space.has_mapping(obj.spaces.configuration_space))
                assert (self.spaces.coordinate_space.has_mapping(obj.spaces.coordinate_space))
            else:
                obj.spaces = self.spaces

            # Initialize the configuration and coordinate if not already done
            if not (hasattr(obj, 'configuration')) or obj.configuration is None:
                obj.configuration = obj.spaces.configuration_space.none()

            # Add the object to the object dictionary
            self.objects[obj.id] = obj

            # Add all the child actions to own actions
            for name, action in self.scheduling.actions.items():
                if name in obj.scheduling.actions and not name.startswith("_"):
                    obj.scheduling.actions[name].parent = action

            logging.info(f"Added Object \"{obj.name}\" {type(obj)} to the world.")

    # ------------------------------------------------------------------------------------------------------------------
    def removeObject(self, objects: Union[list, WorldObject]):
        if not (isinstance(objects, list)):
            objects = [objects]

        for obj in objects:
            assert (isinstance(obj, WorldObject))

            # Remove the object from the object dictionary
            if obj in self.objects.values():
                del (self.objects[obj.id])

            # TODO: Also deregister the simulation object
            self.deregisterChild(obj)

    # ------------------------------------------------------------------------------------------------------------------
    def getObjectsByName(self, name: str, regex=False) -> list:
        objects = []

        if not regex:
            for _, obj in self.objects.items():
                if obj.name == name:
                    objects.append(obj)
        else:
            for _, obj in self.objects.items():
                if re.search(name, obj.name):
                    objects.append(obj)

        return objects

    # ------------------------------------------------------------------------------------------------------------------
    def getObjectsByType(self, type) -> list:
        objects = []

        for _, obj in self.objects.items():
            if isinstance(obj, type):
                objects.append(obj)

        return objects

    # ------------------------------------------------------------------------------------------------------------------
    def physicsUpdate(self):
        for name, obj in self.objects.items():
            if obj.physics is not None:
                obj.scheduling.actions['physics_update']()

    # ------------------------------------------------------------------------------------------------------------------
    def getSample(self) -> dict:
        """
                - newly to world added objects
        - newly from world deleted objects
        - update already existing objects (e.g. their position)
        :return: sample dictionary
        """
        sample = {'world': {}}
        # reset world sample -> clear all objects

        for o in self.objects.values():
            sample['world'][o.id] = o.getSample()

        # # Check for objects that have been added since sending the last sample
        # if not 'world' in self._lastSample:  # First time sending the sample
        #     ...
        #
        # #
        # # sample['added'] = {k: self.sample['world'][k] for k in
        # #                         set(self.sample['world']) - set(tmp_sample)}
        # #
        # # self.sample['deleted'] = {k: tmp_sample[k] for k in
        # #                           set(tmp_sample) - set(self.sample['world'])}
        #
        # self._lastSample = sample
        return sample

    # ------------------------------------------------------------------------------------------------------------------
    def setSize(self, origin: str = 'center', **kwargs):
        ...
        # for dim, value in kwargs.items():
        #     if self.spaces.coordinate_space.hasDimension(dim):
        #         if isinstance(value, (float, int)):
        #             if origin == 'corner':
        #                 value = [0, value]
        #             elif origin == 'center':
        #                 value = [-value / 2, -value / 2]
        #         self.spaces.coordinate_space[dim].limits = value
        #     else:
        #         raise Exception("Cannot set world size: Dimension not known")
        #
        #     if self.spaces.configuration_space.hasDimension(dim):
        #         if isinstance(value, (float, int)):
        #             if origin == 'corner':
        #                 value = [0, value]
        #             elif origin == 'center':
        #                 value = [-value / 2, -value / 2]
        #         self.spaces.configuration_space[dim].limits = value
        #     else:
        #         raise Exception("Cannot set world size: Dimension not known")

    # ------------------------------------------------------------------------------------------------------------------
    def collisionCheck(self):
        """
        this function is going to do all the collision functions: - check if object is even collidable - **check
        spheres() (maybe Dustin already has a function that does exactly that)** check if object/agents  sphere is
        close to an obstacle sphere - do collision checking → if true put collision points into min/max angle - from
        min/max angle create new function that handles the inputs for a robot
        """
        # loop through dict of alle the objects within testbed (real and simulated)
        for key, obj in self.objects.items():
            # is a collision check to be done for this object?
            if obj.collision.settings.check:
                for _, collision_object in self.objects.items():
                    # don't check with the object itself
                    if collision_object is not obj:
                        # check if the other object even is collidable
                        if collision_object.collision.settings.collidable:
                            # Check if the object is in the include list
                            if any(isinstance(collision_object, include_class) for include_class in
                                   obj.collision.settings.includes):
                                # Check if the object is not in the exclude list
                                if not (any(isinstance(collision_object, exclude_class) for exclude_class in
                                            obj.collision.settings.excludes)):
                                    # do proximity sphere check
                                    if obj.physics.collisionCheck(collision_object.physics):
                                        # print('collision')
                                        pass

    def _init(self):
        pass
