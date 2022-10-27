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
        'tank_robot': {
            'BabylonObject': 'TankRobot',
            'config': {

            }
        }
    }

    with open("../../../object_config.json", "w") as output_file:
        json.dump(out, output_file, indent=2)


if __name__ == '__main__':
    main()
