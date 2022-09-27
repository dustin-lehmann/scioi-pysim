import numpy as np


class A:
    def __init__(self, a=0, **kwargs):
        super().__init__()
        print(a)


class B(A):
    def __init__(self, b, *args, **kwargs):
        self.a = b
        super().__init__(*args, **kwargs)
        print(b)


class C(A):
    def __init__(self, c, *args, **kwargs):
        self.a = c
        super().__init__(**kwargs)

        print(c)



class D(C, B):
    def __init__(self,d, **kwargs):
        super().__init__(**kwargs)
        print(d)


if __name__ == '__main__':
    d = D(a=1, b=2, c=3, d=4)
