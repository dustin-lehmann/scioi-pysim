from pynput.keyboard import Key, Listener, Controller

keyboard = Controller()

DoubleShot = False
shot = False


def on_press(key):
    global DoubleShot
    global shot

    if Key.up == key:
        print("UP")



def on_release(key):
    if key == Key.esc:
        print("ESCAPE")
        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()