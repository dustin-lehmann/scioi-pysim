import dataclasses
from abc import ABC

class AbstractBC(ABC):
    def __int__(self):
        pass

class InheritABC(AbstractBC):
    def __init__(self):
        super().__init__()


class Klasse:
    def __int__(self):
        self.list:['AbstractBC'] = dataclasses.field(default_factory=lambda: [AbstractBC])




if __name__ == '__main__':
    ab1 = InheritABC()
    ab2 = InheritABC()

    klasse = Klasse()
    klasse.list = [ab1,ab2]





    print('ende')