import numpy as np


class A:
    def __init__(self):
        self.a = 1

class B:
    def __init__(self):
        self.b = 3
class object:
    liste: [A]
    def __init__(self, argument):
        self.liste = []
        self.liste.append(argument)



if __name__ == '__main__':
    b = B()
    object = object(b)
    print('end')
