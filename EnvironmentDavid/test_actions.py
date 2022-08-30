from scioi_py_core.core.scheduling import *


def function_step(*args, **kwargs):
    print("Action: Step")


def function_input(*args, **kwargs):
    print("Action: Input")


def function_world(a, *args, **kwargs):
    print(f"Action: World {a}")


def main():
    global_value = 3

    action_step = Action(name='step', function=function_step)

    action_input = Action(name='input', function=function_input, parent=action_step, priority=0)

    action_world = Action(name='world', function=function_world, priority=1,
                          lambdas={'a': lambda: global_value*2})

    action_input.registerAction(action_world)
    action_step()


if __name__ == '__main__':
    main()
