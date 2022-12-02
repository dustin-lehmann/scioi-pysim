import pickle

from matplotlib import pyplot as plt
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Helvetica"
})

def main():
    with open("ilc_data.p", "rb") as filehandler:
        data = pickle.load(filehandler)

    fig = plt.figure()
    plt.plot(data['reference'], color='black', label='Reference $r(t)$' )
    for i, trial in enumerate(data['trials']):
        if i%5==0 or True:
            plt.plot(trial['y'], color=[0, 0, 1], alpha=(i + 1) / (len(data['trials']) + 1), label=f"$y_{{{i}}}$")
        elif i == (len(data['trials']) -1):
            plt.plot(trial['y'], color=[0, 0, 1], alpha=(i + 1) / (len(data['trials']) + 1), label=f"$y_{{{i}}}$")
        else:
            plt.plot(trial['y'], color=[0, 0, 1], alpha=(i + 1) / (len(data['trials']) + 1))


    plt.xlabel('Time [t]')
    plt.ylabel(r'Pitch Angle $\theta$ [rad]')
    plt.grid()
    plt.legend()

    plt.show(block=False)
    plt.savefig('ilc_trajectories.pdf')

    fig = plt.figure()

    e_norm_progression = [trial['e_norm'] for trial in data['trials']]
    plt.plot(e_norm_progression)


    plt.xlabel('Trial [-]')
    plt.ylabel(r'Error Norm $||\mathbf{e}_j||_2$  [-]')
    plt.grid()
    plt.savefig('ilc_norm.pdf')
    plt.show()
    pass


if __name__ == '__main__':
    main()
