import numpy as np

def value():
    return {'a':1, 'b':2}
def testfunc():
    a = {'1':0, '2': value()}
    return a


if __name__ == '__main__':
    b = testfunc()
    print(b)
    print('ende')
