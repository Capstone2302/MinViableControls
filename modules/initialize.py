"""Spreadsheet Column Printer

This script allows the user to print to the console all columns in the
spreadsheet. It is assumed that the first row of the spreadsheet is the
location of the columns.

This tool accepts comma separated value files (.csv) as well as excel
(.xls, .xlsx) files.

This script requires that `pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * intialize - make the board go ready
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

    # pi_pwm = gpio.PWM(PWM,100)		#create PWM instance with frequency
    # pi_pwm.start(0)	