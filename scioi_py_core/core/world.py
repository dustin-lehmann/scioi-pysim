import dataclasses
import logging
import re
from abc import ABC, abstractmethod
from typing import Union

import scioi_py_core.core.spaces as core_spaces
import scioi_py_core.core.scheduling as scheduling
import scioi_py_core.core.physics as physics

from scioi_py_core.utils.babylon import setBabylonStatus


# ======================================================================================================================
@dataclasses.dataclass
class CollisionSettings:
    check: bool = False
    collidable: bool = True
    includes: ['WorldObject'] = dataclasses.field(default_factory=lambda: [WorldObject])
    excludes: ['WorldObject'] = dataclasses.field(default_factory=list)


# ======================================================================================================================
@dataclasses.dataclass
class CollisionData:
    settings: CollisionSettings = dataclasses.field(default_factory=CollisionSettings)
    collision_state: bool = False
    collision_objects: list = dataclasses.field(default_factory=list)


# ======================================================================================================================
class WorldObject(scheduling.ScheduledObject):
    world: 'World'

    space: core_spaces.Space
    configuration: core_spaces.State

    space_global: core_spaces.Space
    configuration_global: core_spaces.State

    group: 'WorldObjectGroup'

    physics: physics.PhysicalBody
    collision: CollisionData

    name: str  # Name given by the user
    id: str  # Unique ID of the object in the corresponding world
    object_type: str = 'object'

    static: bool = False  # A static object is not considered in the generation of a sample for an external tool, unless
    # the 'sample_flag' is set

    sample_flag: bool = False

    # === INIT =========================================================================================================
    def __init__(self, name: str = None, world: 'World' = None, group: 'WorldObjectGroup' = None,
                 space: core_spaces.Space = None, *args, **kwargs):

        self.id = f"{type(self).__name__}_{id(self)}"
        self._configuration = None

        super().__init__()

        if not (name is None and hasattr(self, 'name')):
            self.name = name

        self.world = world
        self.group = group

        if self.group is not None and self.group.world is not None:
            self.world = self.group.world

        if space is not None:
            self.space = space

        if self.group is not None and self.group.space is not None:
            self.space = space

        if self.group is not None:
            if hasattr(self.group, 'addObject'):
                self.group.addObject(self)

        if self.world is not None:
            if hasattr(self.world, 'addObject'):
                self.world.addObject(self)

        if self.space is not None:
            self._configuration = self.space.getState()

        self.collision = CollisionData()

        scheduling.Action(name='physics_update', function=self._updatePhysics,
                          lambdas={'config': lambda: self.configuration}, object=self)

    # === PROPERTIES ===================================================================================================
    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        if value is not None and self.space is not None:
            # value = self.space.map(value)
            self.sample_flag = True
            self._configuration.set(value)

    @property
    def configuration_global(self):
        return self.space_global.map(self.configuration)

    @configuration_global.setter
    def configuration_global(self, value):
        raise Exception("Not implemented yet")

    # === METHODS ======================================================================================================
    def getSample(self):
        return self._getSample()

    # ------------------------------------------------------------------------------------------------------------------
    def translate(self, vector, space='local'):
        assert (space == 'local' or space == 'global' or space == self.space or space == self.space_global)
        self.sample_flag = True
        raise Exception("Need to implement")

    # ------------------------------------------------------------------------------------------------------------------
    def rotate(self, rotation, space='local'):
        assert (space == 'local' or space == 'global' or space == self.space or space == self.space_global)
        self.sample_flag = True
        raise Exception("Need to implement")

    # ------------------------------------------------------------------------------------------------------------------
    def getParameters(self):
        return self._getParameters()

    # ------------------------------------------------------------------------------------------------------------------
    def setConfiguration(self, configuration, space='local'):
        assert (space == 'local' or space == 'global' or space == self.space or space == self.space_global)
        self.sample_flag = True
        if space == 'local' or space == self.space:
            self.configuration = configuration
        else:
            self.configuration_global = configuration

    def getConfiguration(self, space='local'):
        assert (space == 'local' or space == 'global' or space == self.space or space == self.space_global)
        if space == 'local' or space == self.space:
            return self.configuration
        else:
            return self.configuration_global

    # ------------------------------------------------------------------------------------------------------------------
    def _onAdd_callback(self):
        ...

    # === ABSTRACT METHODS =============================================================================================
    def _getParameters(self):
        parameters = {
            'object_type': self.object_type,
            'id': self.id,
            'name': self.name,
            'configuration': self.configuration_global.serialize(),
            'class': self.__class__.__name__
        }
        return parameters

    # ------------------------------------------------------------------------------------------------------------------
    def _getSample(self):
        sample = {'id': self.id,
                  'configuration': self.configuration_global.serialize(),
                  'parameters': self.getParameters()
                  }
        return sample

    # === PRIVATE METHODS ==============================================================================================
    def _updatePhysics(self, config=None, *args, **kwargs):
        if not self.static:
            if config is None:
                config = self.configuration_global
            self.physics.update(config=self.configuration_global)

    def _init(self):
        pass

    # === BUILT-INS ====================================================================================================
    def __repr__(self):
        return f"{str(self.configuration)} (global: {str(self.configuration_global)})"


# ======================================================================================================================
class WorldObjectGroup(WorldObject):
    objects: dict[str, WorldObject]
    local_space: core_spaces.Space
    object_type = 'group'

    def __init__(self, name: str = None, world: 'World' = None, objects: list = None,
                 local_space: core_spaces.Space = None,
                 *args, **kwargs):
        super().__init__(name=name, world=world, *args, **kwargs)
        assert (self.space == self.world.space)

        self.collision.settings.collidable = False

        if local_space is not None:
            self.local_space = local_space
            self.local_space.parent = self.world.space
            self.local_space.origin = self.configuration

        self.objects = {}

        if objects is not None:
            for obj in objects:
                self.addObject(obj)

    def addObject(self, object: 'WorldObject'):

        if isinstance(object, WorldObject):
            object = [object]

        for obj in object:
            assert (isinstance(obj, WorldObject))

            # Check if the object already exists in  the list of objects. If so, just raise a warning and continue
            if obj in self.objects.values():
                logging.warning("Object already exists in group")
                continue

            for _, other in self.objects.items():
                if obj.name == other.name:
                    logging.warning(f"There already exists an object with name \"{obj.name}\".")
                    break

            obj.world = self.world

            if self.local_space is not None:
                obj.space = self.local_space

            # Add the object to the object dictionary
            self.objects[obj.id] = obj

            logging.info(f"Added Object \"{obj.name}\" {type(obj)} to the group {self.name}")

    def _updatePhysics(self, config, *args, **kwargs):
        pass


# ======================================================================================================================
class World(scheduling.ScheduledObject):
    space: core_spaces.Space
    objects: dict[str, 'WorldObject']
    agents: dict[str, 'WorldObject']
    name = 'world'
    size: dict  # Add the World Dimensions here and not in the Spaces. This makes it much easier

    # === INIT =========================================================================================================
    def __init__(self, space: core_spaces.Space = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'space'):
            assert (space is not None)
            self.space = space

        self.objects: dict[str, 'WorldObject'] = {}
        self.agents: dict[str, 'WorldObject'] = {}
        self.size = None

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
            obj.space_global = self.space

            # Check if the object has a dedicated space
            if hasattr(obj, 'space') and obj.space is not None:
                # If the object has a dedicated space, make sure that there is a mapping to the global space
                assert (obj.space.hasMapping(self.space))
            else:
                # Add the world's space as the object's space
                obj.space = self.space

            # Add the object to the object dictionary
            self.objects[obj.id] = obj

            logging.info(f"Added Object \"{obj.name}\" {type(obj)} to the world.")

            # Call the onAdd callback
            obj._onAdd_callback()

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
    def addAgent(self, agent: WorldObject):
        self.agents[agent.id] = agent

        if agent.id not in self.objects:
            self.addObject(agent)

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
        sample = {'objects': {}}
        # reset world sample -> clear all objects

        for obj in self.objects.values():
            if not obj.static or (obj.static and obj.sample_flag):
                sample['objects'][obj.id] = obj.getSample()
                obj.sample_flag = False

        return sample

    # ------------------------------------------------------------------------------------------------------------------
    def generateWorldConfig(self):
        world_definition = {'objects': {}}

        for object_id, obj in self.objects.items():
            world_definition['objects'][object_id] = obj.getParameters()

        return world_definition

    # ------------------------------------------------------------------------------------------------------------------
    def setSize(self, **kwargs):
        self.size = {}
        if self.space.hasDimension('pos'):
            self.size['pos'] = {}
            for dim, value in kwargs.items():
                if dim in self.space['pos']:
                    assert (isinstance(value, list))
                    self.size['pos'][dim] = value
        else:
            for dim, value in kwargs.items():
                if self.space.hasDimension(dim):
                    assert (isinstance(value, list))
                    self.size[dim] = value

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
                                        setBabylonStatus('collision')

    def _init(self):
        # TODO: Put this in a subfunction
        # Go over all objects and build the action tree
        for obj_name, obj in self.objects.items():
            for action_name, action in self.scheduling.actions.items():
                if action_name in obj.scheduling.actions and not action_name.startswith("_"):
                    obj.scheduling.actions[action_name].parent = action
