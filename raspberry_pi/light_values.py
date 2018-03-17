"""
A list of RGB values representing real world lighting.

Sourced from http://planetpixelemporium.com/tutorialpages/light.html

# Light Source Kelvin
LIGHT_SOURCE = RGB(R <int>, G <int>, B <int>)
"""
import collections

RGB = collections.namedtuple('RGB', 'r g b')
# Candle 1900
CANDLE = RGB(255, 147, 41)
# 40W Tungsten 2600
TUNGSTEN_40W = RGB(255, 197, 143)
# 100W Tungsten 2850
TUNGSTEN_100W = RGB(255, 214, 170)
# Halogen 3200
HALOGEN = RGB(255, 241, 224)
# Carbon Arc 5200
CARBON_ARC = RGB(255, 250, 244)
# High Noon Sun 5400
HIGH_NOON = RGB(255, 255, 251)
# Direct Sunlight 6000
DIRECT_SUNLIGHT = WHITE = RGB(255, 255, 255)
# Overcast Sky 7000
OVERCAST_SKY = RGB(201, 226, 255)
# Clear Blue Sky 20000
CLEAR_BLUE_SKY = RGB(64, 156, 255)
# Warm Fluorescent
WARM_FLOURESCENT = RGB(255, 244, 229)
# Standard Fluorescent
STANDARD_FLOURESCENT = RGB(244, 255, 250)
# Cool White Fluorescent
COOL_WHITE_FLOURESCENT = RGB(212, 235, 255)
# Full Spectrum Fluorescent
FULL_SPECTRUM_FLOURESCENT = RGB(255, 244, 242)
# Grow Light Fluorescent
GROW_LIGHT_FLOURESCENT = RGB(255, 239, 247)
# Black Light Fluorescent
BLACK_LIGHT_FLOURESCENT  = RGB(167, 0, 255)
# Mercury Vapor
MERCURY_VAPOR = RGB(216, 247, 255)
# Sodium Vapor
SODIUM_VAPOR = RGB(255, 209, 178)
# Metal Halide
METAL_HALIDE = RGB(242, 252, 255)
# High Pressure Sodium
HIGH_PRESSURE_SODIUM = RGB(255, 183, 76)