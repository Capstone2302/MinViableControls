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
DIR = 20
STEP = 21
SW = 22

def homing_sequence():
    while(gpio.input(SW)):
        print("homing")
#This will be called only when the IR sensor says there is a ball 

# do the routine for the stepper motor test, get to the top and then get to the bottom and wait to be called again 