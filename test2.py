
class ParameterObject:
    def __init__(self, x):
        self.value = x

    def __repr__(self):
        return f"{self.value}"



def main():
    a = [1, 2, 3]
    b = 4.0
    c = ParameterObject(2)

    a1 = a
    a2 = a


    a[0] = 50

    print(a1)
    print(a2)

    pass


if __name__ == '__main__':
    main()