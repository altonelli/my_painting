import gpiozero

STATIC = "static"
WAVE = "wave"

class Light(object):
    """Lights object to maintian logic of the state of the lights and
    Gpio ports
    """
    def __init__(self, arg):
        super(Light, self).__init__()
        brightness = 100
        mode = STATIC
        power_state = "OFF"

    def needs_updating(payload):
        if payload['brightness'] != self.payload \
        or payload['mode'] != self.payload \
        or payload['power_state'] != self.power_state:
            return True
        return False

    def update_lights():
        self.payload = payload['brightness']
        self.mode = payload['mode']
        self.on = payload['power_state']
        self.update_board()

    def update_board():
        print(self.payload)
        print(self.mode)
        print(self.power_state)