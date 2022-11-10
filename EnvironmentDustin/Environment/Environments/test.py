import pickle

from matplotlib import pyplot as plt


def main():
    with open("ilc_data.p", "rb") as filehandler:
        data = pickle.load(filehandler)

    fig = plt.figure()
    plt.plot(data['reference'], color='black')
    for i, trial in enumerate(data['trials']):
        plt.plot(trial['y'], color=[0, 0, 1], alpha=(i + 1) / (len(data['trials']) + 1))
    plt.show(block=False)

    fig = plt.figure()

    e_norm_progression = [trial['e_norm'] for trial in data['trials']]
    plt.plot(e_norm_progression)
    plt.show()

    pass


if __name__ == '__main__':
    main()
