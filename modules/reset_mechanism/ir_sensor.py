#code for IR sensor from time import sleep
import RPi.GPIO as gpio
from time import sleep

IR = 16

gpio.setmode(gpio.BCM)
gpio.setup(IR, gpio.IN)

try:
    while(True):
        if gpio.input(IR):
            print("pin 16 is high")
        else:
            print("pin 16 is low")
        sleep(0.5)

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    gpio.cleanup()