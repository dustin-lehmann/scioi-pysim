babylon_settings = {
    'status': '',
    'background_color': 0
}


def setBabylonSettings(**kwargs):
    global babylon_settings
    for key, arg in kwargs.items():
        if key in babylon_settings:
            babylon_settings[key] = arg


def getBabylonSettings():
    global babylon_settings
    return babylon_settings
