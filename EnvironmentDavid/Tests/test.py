class example_object:
    def __init__(self):
        self.size = 10
        self.height = 4
        self.variabkle = 10


class Test:
    testdict: dict
    def __init__(self, *args: example_object, **kwargs):
        self.robotlist = {}

        for element in args:
            self.robotlist(element)
            print('args element')

        for element in kwargs:
            print('kwargs element')


if __name__ == '__main__':
    obj = example_object()
    obj2 = example_object()
    test = Test(obj, obj2)
    print(test.robotlist[0].size)
    obj.size = 3
    print(test.robotlist[0].size)

    print('ende')