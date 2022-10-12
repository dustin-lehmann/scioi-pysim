import numpy as np

if __name__ == '__main__':
    buch = {'a': 1, 'b': {1, 2, 3}, 'c': 0}
    buch['a'] = [1, 2, 3]

    buch['a'] = [1, 2, 3]

    for elements in buch['a']:
        print(buch['a'][elements])

    print('ende')
