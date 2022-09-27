import dataclasses
from abc import ABC
from EnvironmentDavid.baseline.baseline_environment import BayblonVisualization

class A:
    def __init__(self,a, **kwargs):
        # super(A,self).__init__(**kwargs)
        self.a = a
        print(self.a)


class B(A):
    def __init__(self, b, **kwargs):
        super(B,self).__init__(**kwargs)
        self.b = b
        print(self.b)

class C(A):
    def __init__(self,c, **kwargs):
        super(C, self).__init__(**kwargs)
        self.c = c
        print(c)

class D(B,C):
    def __init__(self):
        super()

if __name__ == '__main__':
    # babylon_env = BayblonVisualization()
    #
    # babylon_env.start_babylon()
    test = C(a=1,b=2,c=3)


    print('ende')
