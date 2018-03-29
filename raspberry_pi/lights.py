"""
Logic between the Raspberry Pi and the LED light. Changes maintained through
the Light object and the pigpio daemon connection.
"""
import time
import logging

import pigpio

from light_values import RGB, NATURALISH

# Respective Gpio ports
R_PIN = 4
G_PIN = 17
B_PIN = 22

# Gpio ports representation in RGB tuple
PINS = RGB(r=R_PIN, g=G_PIN, b=B_PIN)

# OFF color setting to turn lights off
OFF = RGB(r=0, g=0, b=0)

# Logger information
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

class Light(object):
    """
    Light object to maintian logic of the state of the lights and
    Gpio ports
    """
    def __init__(self):
        super(Light, self).__init__()
        ## Default start up settings
        self.current_brightness = 100 # current display brightness
        self.brightness = 100 # brightness setting based on shadow
        self.color = NATURALISH
        self.power_state = "OFF"

        # Establish connection to pigpio daemon
        self.pi = pigpio.pi()

    def current_settings(self):
        """
        Gives current settings of Light object.

        Returns:
            Python dict of Light object power state and brightness
        """
        return {
                   'power_state': self.power_state,
                   'brightness': self.brightness,
               }

    def needs_updating(self, light_data):
        """
        Determines if Light object needs to update its settings based on new
        light data.

        Args:
            light_data: Python dict of new light data to represent
        Returns:
            boolean
        """
        if light_data.get('brightness') != self.brightness \
        or light_data.get('power_state') != self.power_state:
            return True
        return False

    def update_lights(self, light_data):
        """
        Updates Light object needs to update its settings. Sets
        current brightness to old brightness setting before updating brightness
        and power_state. Will update brightness and current brightness even
        if in off state.

        Args:
            light_data: Python dict of new light data to represent
        Returns:
            boolean
        """
        self.current_brightness = self.brightness
        self.brightness = light_data.get('brightness')
        self.power_state = light_data.get('power_state')
        self._update_board()

    def _update_board(self):
        """
        Updates light brightness if power state is on. Otherwise sets the
        lights to OFF color. Logs current settings after updating.

        Args:
            None
        """
        if self.power_state == "ON":
            # Only update brightness if on. Will adjust from most recent brightness level.
            self._update_brightness()
        else:
            # Case where called to switch off
            self._update_color(OFF)
        logger.info(self.power_state)
        logger.info(self.brightness)

    def _update_brightness(self):
        """
        Adjusts brightness level incrementally. Will begin from current
        brightness even if brightness change in off state. Gradually
        changes current brightness until equal to brightness setting
        updating the lights with each change.

        Args:
            None
        """
        while self.current_brightness != self.brightness:
            next_color = RGB(r=int(self.color.r * (self.current_brightness/100.0)),
                             g=int(self.color.g * (self.current_brightness/100.0)),
                             b=int(self.color.b * (self.current_brightness/100.0)))
            self._update_color(next_color)
            diff = self.brightness - self.current_brightness
            # adjust current brightness to +/- 1
            self.current_brightness = self.current_brightness + \
                (diff) / abs(diff)
            time.sleep(.05)
        # Final update to exact brightness and default if no change in brightness setting
        final_color = RGB(r=int(self.color.r * (self.brightness/100.0)),
                          g=int(self.color.g * (self.brightness/100.0)),
                          b=int(self.color.b * (self.brightness/100.0)))
        self._update_color(final_color)

    def _update_color(self, rgb_tuple):
        """
        Sets lights to color in rgb_tuple by setting all RGB gpio ports to
        the respective color.

        Args:
            rgb_tuple: RGB tuple of colors to represent
        """
        for color in rgb_tuple._fields:
            pin = getattr(PINS, color)
            value = getattr(rgb_tuple, color)
            # Ensure color between 0 and 255
            value = max(min(value, 255), 0)
            # print(pin, value)
            self.pi.set_PWM_dutycycle(pin, value)


# Demo of fade effect for lights
if __name__ == '__main__':
    light = Light()
    light._update_board()
    time.sleep(1)
    light_data_0 = {
        'power_state': "ON",
        'brightness': 100,
    }
    light.update_lights(light_data_0)
    time.sleep(1)
    light_data_1 = {
        'power_state': "ON",
        'brightness': 50,
    }
    light.update_lights(light_data_1)
    time.sleep(1)
    light_data_2 = {
        'power_state': "ON",
        'brightness': 10,
    }
    light.update_lights(light_data_2)
    time.sleep(1)
    light_data_3 = {
        'power_state': "ON",
        'brightness': 100,
    }
    light.update_lights(light_data_3)
    time.sleep(1)
    light_data_4 = {
        'power_state': "OFF",
        'brightness': 100,
    }
    light.update_lights(light_data_4)