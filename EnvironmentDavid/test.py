import numpy as np

if __name__ == '__main__':
    babylon = {'a': [], 'b': {1, 2, 3}, 'c': 0}
    world = {'a': [], 'c': 0}

    shared_items = {k: babylon[k] for k in babylon if k not in world}
    # shared_items = {k: babylon[k] for k in babylon if k in world and babylon[k] == world[k]}

    added_items = {k : world[k] for k in set(world) - set(babylon)}

    deleted_items = {k: babylon[k] for k in set(babylon) - set(world)}

    test3 = babylon | world

    print('ende')
