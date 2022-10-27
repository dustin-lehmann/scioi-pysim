import scioi_py_core.core as core
import json


def generateWorldDefinition(world: core.world.World, output_file: str = None):
    world_definition = {'objects': {}}

    for object_id, obj in world.objects.items():
        world_definition['objects'][object_id] = obj.getParameters()

    dict_out = json.dumps(world_definition, default=core.spaces.dumper)

    if output_file is not None:
        with open(output_file, 'w') as f:
            json.dump(world_definition, f, default=core.spaces.dumper, indent=2)

    return dict_out
