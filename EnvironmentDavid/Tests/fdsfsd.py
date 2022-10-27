import asyncio
import time

from EnvironmentDavid.babylon import BABYLON_LiveBackend


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    webapp = BABYLON_LiveBackend("../babylon/pysim_env.html", options={})
    webapp.start()
    while True:
        time.sleep(0.1)


if __name__ == '__main__':
    main()