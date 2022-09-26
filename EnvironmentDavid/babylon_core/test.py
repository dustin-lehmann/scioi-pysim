import numpy as np


class Test:
    def __init__(self, var= 5, var2 = 2434):
        self.x = var
        self.var2 = var2
        print(self.x, self.var2)


class Test2(Test):
    def __init__(self, *args, **kwargs):
        test2 = kwargs
        super().__init__(*args, **kwargs)


class Test3(Test2):
    def __init__(self, *args, **kwargs):
        print(kwargs['var'])
        test3 = kwargs

        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    orientation=np.eye(3)
