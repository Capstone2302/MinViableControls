#code for testing the main motor, high priority , med diffuculty

from time import sleep
import RPi.GPIO as gpio

DIR = 6
PWM = 13
CW =1
CCW =0

gpio.setmode(gpio.BCM)
gpio.setup(DIR, gpio.OUT)
gpio.setup(PWM, gpio.OUT)
gpio.output(DIR,CW)

pi_pwm = gpio.PWM(PWM,100)		#create PWM instance with frequency
pi_pwm.start(0)			
# Main body of code
try:
    while True:
        sleep(2)
        gpio.output(DIR,CW)
        for duty in range(0,101,1):
            pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
            sleep(0.01) 
        pi_pwm.ChangeDutyCycle(0) #breaking (check the pwm out put when writing 0 vs just not writing anything)
        sleep(5)


        pi_pwm.ChangeDutyCycle(0)
        gpio.output(DIR,CCW)
        for duty in range(0,101,1):
            pi_pwm.ChangeDutyCycle(duty)
            sleep(0.01)

        pi_pwm.ChangeDutyCycle(0)
        
        sleep(5)


              
        
except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    gpio.cleanup()