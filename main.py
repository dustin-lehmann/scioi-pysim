class Wall:
    object_type = 'wall'


class Wall_rot(Wall):
    object_type = 'wall_rot'

class Wall_rot_special(Wall_rot):
    ...

def main():
    x = Wall()

    pass

if __name__ == '__main__':
    main()
