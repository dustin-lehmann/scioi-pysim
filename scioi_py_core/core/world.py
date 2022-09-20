import dataclasses
import logging
import re
from abc import ABC, abstractmethod
from typing import Union

from ..core import spaces as spaces
from ..core import physics as physics
from ..core import scheduling as scheduling


# TODO: Should this be a scheduled object if it can be simulated and real? Probably yes, but not simulated object.
#  There has to be a switch somewhere telling that this is real and this not

@dataclasses.dataclass
class CollisionSettings:
    check: bool = False
    collidable: bool = True
    includes: ['WorldObject'] = dataclasses.field(default_factory=lambda: [WorldObject])
    excludes: ['WorldObject'] = dataclasses.field(default_factory=list)


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

    # === INIT =========================================================================================================
    def __init__(self, name: str = None, world: 'World' = None, collision_includes: [] = None,
                 collision_excludes: [] = None, collision_check: bool = False, collidable: bool = True, *args,
                 **kwargs):
        print(name)
        super().__init__()
        self.name = name
        self.world = world

        self.collision = CollisionState()
        self.collision.settings.check = collision_check
        self.collision.settings.collidable = collidable
        if collision_includes is not None:
            self.collision.settings.includes = collision_includes
        if collision_excludes is not None:
            self.collision.settings.excludes = collision_excludes

        # self.configuration = None

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
            # if not (hasattr(obj, 'configuration')) or obj.configuration is None:
            #     obj.configuration = self.spaces.configuration_space.zeros()

            # Give the object an id
            obj.id = f"{type(obj)}_{id(obj)}"

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
    def collisionCheck(self):
        """
        this function is going to do all the collision functions: - check if object is even collidable - **check
        spheres() (maybe Dustin already has a function that does exactly that)** check if object/agents  sphere is
        close to an obstacle sphere - do collision checking → if true put collision points into min/max angle - from
        min/max angle create new function that handles the inputs for a robot
        """
        # loop through dict of alle the objects within testbed (real and simulated)
        for key, obj in self.objects.items():
            # collision check is supposed to be done
            if obj.collision.settings.check:
                for _, collision_object in self.objects.items():
                    if collision_object is not obj:
                        # check if object even is collidable
                        if collision_object.collision.settings.collidable:
                            # Check if the object is in the include list
                            if any(isinstance(collision_object, include_class) for include_class in
                                   obj.collision.settings.includes):
                                # Check if the object is not in the exclude list
                                if not (any(isinstance(collision_object, exclude_class) for exclude_class in
                                            obj.collision.settings.excludes)):
                                    # do sphere check
                                    print('add sphere check!')
                                    ...

    def _init(self):
        pass
