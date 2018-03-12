# import gpiozero

STATIC = "STATIC"
WAVE = "WAVE"

class Light(object):
    """Lights object to maintian logic of the state of the lights and
    Gpio ports
    """
    def __init__(self):
        super(Light, self).__init__()
        self.brightness = 100
        self.mode = STATIC
        self.power_state = "OFF"

    def current_settings(self):
        return {
                   'power_state': self.power_state,
                   'brightness': self.brightness,
                   'mode': self.mode
               }

    def needs_updating(self, light_data):
        if light_data.get('brightness') != self.brightness \
        or light_data.get('mode') != self.mode \
        or light_data.get('power_state') != self.power_state:
            return True
        return False

    def update_lights(self, light_data):
        self.brightness = light_data.get('brightness')
        self.mode = light_data.get('mode')
        self.power_state = light_data.get('power_state')
        print(self.mode,self.mode)
        self.update_board()

    def update_board(self):
        print(self.brightness)
        print(self.mode)
        print(self.power_state)