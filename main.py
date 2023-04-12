"""Main Script

This runs the main control loop for the wheel. Calls the homing, elevator, initialize and controll functions/files.

"""
import RPi.GPIO as gpio
from modules.initialize import init_board
from modules.elevator_routine import homing_sequence, elevator_routine
from modules.controller import Controller

#TODO: Homing sequence
#TODO: Make look up table (?) someway of not constantly re intializing the values
IR = 16

# gpio.setmode(gpio.BCM)
# gpio.setup(IR, gpio.IN)


init_board()
print("init done")
homing_sequence()
print("at switch")
controller = Controller()
try:
    while(True):
        if (gpio.input(IR) == False):
            elevator_routine()
        # print(gpio.input(IR))
        controller.control_routine()


except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    gpio.cleanup()

