import pickle

import numpy as np
from matplotlib import pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Helvetica"
})


def main():
    with open("ilc_data.p", "rb") as filehandler:
        data = pickle.load(filehandler)

    fig = plt.figure()
    plt.plot(data['reference'], color='black', label='Reference $r(t)$')
    for i, trial in enumerate(data['trials']):
        if i % 5 == 0:
            plt.plot(trial['y'], color=[61 / 255, 82 / 255, 149 / 255], alpha=(i + 1) / (len(data['trials']) + 1), label=f"$y_{{{i}}}$")
        elif i == (len(data['trials']) - 1):
            plt.plot(trial['y'], color=[61 / 255, 82 / 255, 149 / 255], alpha=(i + 1) / (len(data['trials']) + 1), label=f"$y_{{{i}}}$")
        else:
            plt.plot(trial['y'], color=[61 / 255, 82 / 255, 149 / 255], alpha=(i + 1) / (len(data['trials']) + 1))

    plt.xlabel('Time [t]')
    plt.ylabel(r'Pitch Angle $\theta$ [rad]')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)
    plt.savefig('ilc_trajectories.png')

    fig = plt.figure()

    e_norm_progression = [trial['e_norm'] for trial in data['trials']] / data['trials'][0]['e_norm']
    plt.plot(e_norm_progression, label='Agent 1 (individual)',
             color=[61 / 255, 82 / 255, 149 / 255], linestyle = ':', marker = 'o', markersize = 4)


    plt.xlabel('Trial $j$ [-]')
    plt.ylabel(r'Normalized Error Norm $||\mathbf{e}_j||_2 / ||\mathbf{e}_0||_2$  [-]')
    plt.xticks(np.arange(0,len(data['trials']), 1))
    plt.grid()
    plt.tight_layout()
    plt.ylim(0,1)
    plt.savefig('ilc_norm.png')
    plt.show()
    pass


if __name__ == '__main__':
    main()
