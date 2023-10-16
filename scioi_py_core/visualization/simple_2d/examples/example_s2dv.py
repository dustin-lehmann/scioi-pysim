import time

from scioi_py_core.visualization.simple_2d.simple_2d_visualization import Simple2DVisualization


def example_s2dv():
    vis = Simple2DVisualization()
    vis.init(size_x = [-2.5,2.5], size_y=[-2.5,2.5])
    agent = vis.add_agent()
    agent.update(-1,-1,2)
    vis.start()

    time.sleep(10)


if __name__ == '__main__':
    example_s2dv()