import dataclasses
import logging
import re
from abc import ABC, abstractmethod
from typing import Union

from ..core import spaces as spaces
from ..core import physics as physics
from ..core import scheduling as scheduling
from scioi_py_core.utils.orientations import psiFromRotMat


# TODO: Should this be a scheduled object if it can be simulated and real? Probably yes, but not simulated object.
#  There has to be a switch somewhere telling that this is real and this not

@dataclasses.dataclass
class CollisionSettings:
    check: bool = False
    collidable: bool = True
    _includes: ['WorldObject'] = dataclasses.field(default_factory=lambda: [WorldObject])
    _excludes: ['WorldObject'] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class CollisionState:
    settings: CollisionSettings = dataclasses.field(default_factory=CollisionSettings)
    collision_state: bool = False
    collision_objects: list = dataclasses.field(default_factory=list)


# ======================================================================================================================
class WorldObject(scheduling.ScheduledObject):
    world: 'World'
    physics: physics.PhysicalBody
    collision: CollisionState
    coordinate: spaces.State
    configuration: spaces.State

    name: str  # Name given by the user
    id: str  # Unique ID of the object in the corresponding world
    object_type: str = 'object'

    # === INIT =========================================================================================================
    def __init__(self, name: str = None, world: 'World' = None, collision_includes: [] = None,
                 collision_excludes: [] = None, collision_check: bool = False, collidable: bool = True, *args,
                 **kwargs):

        self.id = f"{type(self)}_{id(self)}"
        super().__init__()
        self.name = name
        self.world = world

        self.collision = CollisionState()
        self.collision.settings.check = collision_check
        self.collision.settings.collidable = collidable
        if collision_includes is not None:
            self.collision.settings._includes = collision_includes
        if collision_excludes is not None:
            self.collision.settings._excludes = collision_excludes

        scheduling.Action(name='physics_update', function=self.action_physics_update,
                          lambdas={'config': lambda: self.configuration}, object=self)

        if self.world is not None:
            if hasattr(world, 'addObject'):
                world.addObject(self)

    # === PROPERTIES ===================================================================================================

    @property
    def coordinate(self):
        return self.world.spaces.coordinate_space.map(self.configuration)

    @coordinate.setter
    def coordinate(self, value):
        raise Exception("Setting coordinate is not implemented yet. Set the configuration instead.")

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        if value is not None:
            value = self.world.spaces.configuration_space.map(value)

        self._configuration = value

    # === METHODS ======================================================================================================
    def getSample(self):
        sample = {'name': self.name,
                  'class': self.__class__.__name__,
                  'object_type': self.object_type,
                  # 'position': {'x': self.configuration.value[0], 'y': self.configuration.value[1],
                  #              'z': self.configuration.value[2]},
                  # 'psi': psiFromRotMat(self.configuration.value[3]),
                  'parameters': self.sample_params
                  }
        return sample

    # ------------------------------------------------------------------------------------------------------------------
    @property
    @abstractmethod
    def sample_params(self):
        """
        this function is supposed to be tailored to each different class type since the can have specific parameters
        relevant for babylon
        :return: specific object parameters
        """
        params = {}
        return params

    # === ACTIONS ======================================================================================================
    @abstractmethod
    def action_physics_update(self, config, *args, **kwargs):
        pass

    def _init(self):
        pass


# ======================================================================================================================
@dataclasses.dataclass
class WorldSpaces:
    coordinate_space: spaces.Space = None
    configuration_space: spaces.Space = None
    map_configToCoordinateSpace: spaces.Mapping = None


# ======================================================================================================================
class World(scheduling.ScheduledObject):  # TODO: should this be a scheduled object?
    spaces: WorldSpaces
    objects: dict[str, 'WorldObject']

    # === INIT =========================================================================================================
    def __init__(self, spaces: WorldSpaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spaces = spaces
        self.objects: dict[str, 'WorldObject'] = {}
        self.sample = {'world': {},
                       'added': {},
                       'deleted': {},
                       }

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

            # Initialize the configuration and coordinate if not already done
            if not (hasattr(obj, 'configuration')) or obj.configuration is None:
                obj.configuration = self.spaces.configuration_space.none()

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
    def create_world_sample(self) -> dict:
        """
                - newly to world added objects
        - newly from world deleted objects
        - update already existing objects (e.g. their position)
        :return: sample dictionary
        """
        tmp_sample = self.sample['world']
        # reset world sample -> clear all objects
        self.sample['world'] = {}

        for o in self.objects.values():
            self.sample['world'][o.id] = o.getSample()

        self.sample['added'] = {k: self.sample['world'][k] for k in
                                set(self.sample['world']) - set(tmp_sample)}

        self.sample['deleted'] = {k: tmp_sample[k] for k in
                                  set(tmp_sample) - set(self.sample['world'])}

        return self.sample

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
                                   obj.collision.settings._includes):
                                # Check if the object is not in the exclude list
                                if not (any(isinstance(collision_object, exclude_class) for exclude_class in
                                            obj.collision.settings._excludes)):
                                    # do proximity sphere check
                                    if obj.physics.collisionCheck(collision_object.physics):
                                        print('collision')
                                        # pass

    def _init(self):
        pass
