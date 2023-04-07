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

    * get_spreadsheet_cols - returns the column headers of the file
    * main - the main function of the script
"""

#TODO: Update documentation
import RPi.GPIO as gpio
from time import sleep

SW = 22

DIR = 21
STEP = 20
CW =1
CCW =0

gpio.setmode(gpio.BCM)
gpio.setup(DIR, gpio.OUT)
gpio.setup(STEP, gpio.OUT)
gpio.output(DIR,CW)

gpio.setmode(gpio.BCM)
gpio.setup(SW, gpio.IN)

def homing_sequence():
        while(True):
            gpio.output(DIR,CW) #2300
            for x in range(50):
                gpio.output(STEP,gpio.HIGH)
                sleep(.00100)
                gpio.output(STEP,gpio.LOW)
                sleep(.00100)
            if gpio.input(SW):
                print("closed")
                gpio.cleanup()
                break

def elevator_routine():
    gpio.output(DIR,CCW)
    for x in range(2000): #2300
        gpio.output(STEP,gpio.HIGH)
        sleep(.000500)
        gpio.output(STEP,gpio.LOW)
        sleep(.000500)
    for x in range(280): #2300
        gpio.output(STEP,gpio.HIGH)
        sleep(.00100)
        gpio.output(STEP,gpio.LOW)
        sleep(.00100)    
    sleep(0.4)
    gpio.output(DIR,CW) #2300
    for x in range(2325):
        gpio.output(STEP,gpio.HIGH)
        sleep(.000300)
        gpio.output(STEP,gpio.LOW)
        sleep(.000300)

        
#This will be called only wh
# en the IR sensor says there is a ball 

# do the routine for the stepper motor test, get to the top and then get to the bottom and wait to be called again 