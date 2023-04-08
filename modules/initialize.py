""" Initializing the board


    * intialize - make the board 
"""

#TODO: update documentation
#TODO: call these variables from somehwre or make them callable.

import RPi.GPIO as gpio

def init_board():
    SW = 22
    IR = 16
    DIR = 21
    STEP = 20
    DIR_M = 6
    PWM = 13

    gpio.setmode(gpio.BCM)
    gpio.setup(SW, gpio.IN)

    gpio.setmode(gpio.BCM)
    gpio.setup(IR, gpio.IN)

    gpio.setmode(gpio.BCM)
    gpio.setup(DIR, gpio.OUT)
    gpio.setup(STEP, gpio.OUT)
    
    gpio.setmode(gpio.BCM)
    gpio.setup(DIR_M, gpio.OUT)
    gpio.setup(PWM, gpio.OUT)