#code for switch testing, med prioirty low difficulty
import RPi.GPIO as gpio
from time import sleep

SW = 22

gpio.setmode(gpio.BCM)
gpio.setup(SW, gpio.IN)

try:
    while(True):
        if gpio.input(SW):
            print("switch closed")
        else:
            print("open")
        sleep(0.5)

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    gpio.cleanup()
