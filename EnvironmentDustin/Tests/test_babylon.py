import time

from scioi_py_core.visualization.babylon.babylon import BabylonVisualization, babylon_path


def main():
    webapp = babylon_path + 'pysim_env.html'

    config = {
        'a': 3,
        'b': "Hallo"
    }

    vis = BabylonVisualization(webapp=webapp)
    vis.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
