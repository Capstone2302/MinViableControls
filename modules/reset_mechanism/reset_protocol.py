# this is where the reset logic will go
import RPi.GPIO as gpio

IR = 16

gpio.setmode(gpio.BCM)
gpio.setup(IR, gpio.IN)


#homing sequence

def elevator_routine():
    print("oops")

while(True):
        if (gpio.input(IR)):
              elevator_routine()
