"""Main Script

This runs the main control loop for the wheel. Calls the homing, elevator, initialize and controll functions/files.

"""
import RPi.GPIO as gpio
from modules.initialize import init_board
from modules.elevator_routine import homing_sequence, elevator_routine

#TODO: intilize board
#TODO: Homing sequence
#TODO: while true loop

SW = 22
init_board()
# homing_sequence()
try:
    while(True):
        if(gpio.input(SW) == False):
            elevator_routine()

        else:
            print("print no ball")

            
except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    gpio.cleanup()

