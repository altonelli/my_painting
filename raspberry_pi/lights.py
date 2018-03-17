import time

import pigpio

from light_constants import *

STATIC = "STATIC"
WAVE = "WAVE"

R_PIN = 17
G_PIN = 22
B_PIN = 4

PINS = RGB(r=R_PIN, g=G_PIN, b=B_PIN)

VCC = 10

OFF = RGB(r=0, g=0, b=0)

class Light(object):
    """Lights object to maintian logic of the state of the lights and
    Gpio ports
    """
    def __init__(self):
        super(Light, self).__init__()
        self.previous_brightness = 100
        self.brightness = 100
        self.color = CANDLE
        self.mode = STATIC
        self.power_state = "OFF"

        self.pi = pigpio.pi()

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
        self.previous_brightness = self.brightness
        self.brightness = light_data.get('brightness')
        self.mode = light_data.get('mode')
        self.power_state = light_data.get('power_state')
        self._update_board()

    def _update_board(self):
        if self.power_state == "ON":
            # Case where called on and no change in brightness
            # if self.previous_brightness == self.brightness:
            #     gpio_brightness = self.previous_brightness * (255/100)
            #     self.pi.set_PWM_dutycycle(PIN, gpio_brightness)
            # # Case where already on and need change in brightness
            # else:
            self._update_brightness()
        else:
            # Case where called off
            self._update_color(OFF)
        print(self.brightness)
        print(self.mode)
        print(self.power_state)

    def _update_brightness(self):
        while self.previous_brightness != self.brightness:
            next_color = RGB(r=int(self.color.r * (self.previous_brightness/100)),
                             g=int(self.color.g * (self.previous_brightness/100)),
                             b=int(self.color.b * (self.previous_brightness/100)))
            self._update_color(next_color)
            diff = self.brightness - self.previous_brightness
            # adjust previous brightness to +/- 1
            self.previous_brightness = self.previous_brightness + \
                (diff) / abs(diff)
            time.sleep(.05)
        final_color = RGB(r=int(self.color.r * (self.brightness/100)),
                         g=int(self.color.g * (self.brightness/100)),
                         b=int(self.color.b * (self.brightness/100)))
        self._update_color(self.color)

    def _update_color(self, rgb_tuple):
        for color in rgb_tuple._fields:
            self.pi.set_PWM_dutycycle(getattr(PINS, color), getattr(rgb_tuple, color))

def update_color(pi, rgb_tuple):
    for color in rgb_tuple._fields:
        pi.set_PWM_dutycycle(getattr(PINS, color), getattr(rgb_tuple, color))

if __name__ == '__main__':
    light = Light()
    light._update_board()
    time.sleep(3)
    light_data_0 = {
        'power_state': "ON",
        'brightness': 100,
        'mode': STATIC
    }
    light.update_lights(light_data_0)
    time.sleep(3)
    light_data_1 = {
        'power_state': "ON",
        'brightness': 50,
        'mode': STATIC
    }
    light.update_lights(light_data_1)
    time.sleep(7)
    light_data_2 = {
        'power_state': "ON",
        'brightness': 10,
        'mode': STATIC
    }
    light.update_lights(light_data_2)
    time.sleep(10)
    light_data_3 = {
        'power_state': "ON",
        'brightness': 100,
        'mode': STATIC
    }
    light.update_lights(light_data_3)
    time.sleep(7)
    light_data_4 = {
        'power_state': "OFF",
        'brightness': 100,
        'mode': STATIC
    }
    light.update_lights(light_data_4)
    return 0