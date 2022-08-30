import scioi_py_core.core.dynamics as dynamics
from scioi_py_core.core import spaces as sp


def example_1():
    # Define simple one dimensional dynamics
    state_space = dynamics.sp.Space(dimensions=['x'])
    input_space = dynamics.sp.Space(dimensions=['v'])
    output_space = state_space
    integrator_spaces = dynamics.DynamicsSpaces(state_space, input_space, output_space)

    class Integrator(dynamics.Dynamics):
        spaces = integrator_spaces

        def _output(self, state: sp.State):
            return state

        def _dynamics(self, state: sp.State, input: sp.State):
            new_state = state + self.Ts * input
            return new_state

        def _init(self):
            pass

    integrator = Integrator(name='Integrator 1', state=[1], Ts=0.2)
    integrator.input = 1
    print(f"Initial state: {integrator.state}")
    for i in range(0, 10):
        integrator.update()
        print(f"t={integrator.Ts * (i + 1):.2f}: {integrator.state}")


if __name__ == '__main__':
    example_1()
