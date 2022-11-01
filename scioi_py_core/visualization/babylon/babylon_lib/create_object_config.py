import json


def main():
    out = {
        'obstacle': {
            'BabylonObject': 'PysimBox',
            'config': {
                'color': [1, 0, 0],
                'texture': '',
            }
        },
        'floor_tile': {
            'BabylonObject': 'PysimBox',
            'config': {
                'color': [0.7, 0.7, 0.7],
                'texture': '/textures/material/floor_bright.png',
            }
        },
        'tank_robot': {
            'BabylonObject': 'PysimBox',
            'config': {
                'color': [0, 1, 0],
            }
        },
        'twipr_agent': {
            'BabylonObject': 'PysimBox',
            'config': {
                'color': [0, 0, 1],
            }
        }
    }

    with open("object_config.json", "w") as output_file:
        json.dump(out, output_file, indent=2)


if __name__ == '__main__':
    main()