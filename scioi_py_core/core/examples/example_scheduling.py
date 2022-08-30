import logging

from scioi_py_core.core import scheduling as scheduling

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  %(levelname)-8s  %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def example_actions():
    print("--- Example Actions")

    # define an example function that prints the input
    def function1(value):
        print(f"Hello {value}")

    # Build a simple action
    action_simple = scheduling.Action(function=function1)
    action_simple("1")

    # Build an action with a default parameter
    action_default = scheduling.Action(function=function1, parameters={'value': 2})
    action_default()

    # Build an action with a lambda
    action_lambda = scheduling.Action(function=function1, lambdas={'value': lambda: new_value})
    new_value = 3
    action_lambda()
    new_value = 4
    action_lambda()


def example_phases():
    print("--- Example Phases")
    # Define a phase
    phase = scheduling.Action(name='Phase 1')

    # Define an example function
    def function2(value1, value2):
        print(f"{value1=}, {value2=}")

    # Define two actions
    action1 = scheduling.Action(name="Action 1", function=function2, parameters={'value1': "Action 1"},
                                lambdas={'value2': lambda: global_value}, priority=2)
    action1.parent = phase
    #
    # # Define a second action. This time put the parent in the definition of the object
    action2 = scheduling.Action(name='Action 2', function=function2, parameters={'value1': "Action 2"},
                                lambdas={'value2': lambda: global_value},
                                parent=phase, priority=1)

    # # Run the phase
    global_value = 1
    phase()


def example_multiple_phases():
    print("--- Example multiple phases")

    # Define the root phase
    phase_root = scheduling.Action(name='phase_root', function=lambda *args, **kwargs: print("Entering Root Phase"))

    # Define two other phases
    phase_1 = scheduling.Action(name='phase_1', function=lambda *args, **kwargs: print("Entering Phase 1"),
                                parent=phase_root, priority=1)
    phase_2 = scheduling.Action(name='phase_2', function=lambda *args, **kwargs: print("Entering Phase 2"),
                                parent=phase_root, priority=2)

    # Define regular actions
    action_11 = scheduling.Action(name='Action 1-1', function=lambda *args, **kwargs: print(f"Action 1-1 ({args[0]})"),
                                  parent=phase_1)
    action_12 = scheduling.Action(name='Action 1-2', function=lambda *args, **kwargs: print(f"Action 1-2 ({args[1]})"),
                                  parent=phase_1)
    action_21 = scheduling.Action(name='Action 2-1',
                                  function=lambda *args, **kwargs: print(f"Action 2-1 ({kwargs['x']})"), parent=phase_2)

    # Run the Root Phase
    phase_root(12, 'test', x=3)


def example_scheduled_objects():
    print("--- Example Scheduled Objects")
    # Define a scheduled object
    object1 = scheduling.ScheduledObject(name="Object 1")

    # Define a phase and an action for Object 1
    phase_1 = scheduling.Action(name="Phase 1-1", object=object1)
    action_11 = scheduling.Action(name="Function 1-1", function=lambda: print("Action 1-1"), parent=phase_1, priority=2)
    action_12 = scheduling.Action(name="Function 1-2", function=lambda: print("Action 1-2"), parent=phase_1, priority=1)

    # Define a second object and an action
    object2 = scheduling.ScheduledObject(name="Object 2", parent=object1)
    action_2 = scheduling.Action(name="Action 2-1", function=lambda: print("Action 2"), object=object2, priority=3)

    # one can also set the parent phase by referencing over the object
    action_2.parent = object1.scheduling.actions['Phase 1-1']

    object1.scheduling.actions['Phase 1-1']()

    object1.scheduling.tick_global = 5
    print(object2.scheduling.tick_global)


def example_scheduler():
    # Define a simple action
    tick = 0

    def function():
        nonlocal tick
        tick = tick + 1
        logging.info(f"{tick=}")

    action = scheduling.Action(function=function)

    # Define a scheduler
    sched = scheduling.Scheduler(action=action, mode='rt', Ts=0.1)

    # Run the scheduler
    sched.run(steps=10)


if __name__ == '__main__':
    example_actions()
    example_phases()
    example_multiple_phases()
    example_scheduled_objects()
    # example_scheduler()
