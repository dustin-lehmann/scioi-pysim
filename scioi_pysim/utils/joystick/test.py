import scioi_pysim.utils.joystick.joystick as joystick


def testfun(*args, **kwargs):

    print("HELLO" + str(kwargs['a']))


js = joystick.Joystick()

js.set_callback(0, testfun, a=5)
