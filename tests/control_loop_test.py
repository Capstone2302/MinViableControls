import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')

from simple_pid import PID
# Set up GPIO for PWM output
DIR = 6
PWM = 13
CW =1
CCW =0

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.output(DIR,CW)

pi_pwm = GPIO.PWM(PWM,500)		#create PWM instance with frequency
pi_pwm.start(0)	

# Define PID parameters
kp = 10
ki = 0.1
kd = 1

# Set desired position
setpoint = 320  # Replace with your desired position

# Initialize PID controller
pid = PID(kp, ki, kd, setpoint)

# initialize camera
cap = cv2.VideoCapture(0)

# Define range of silver color in HSV format
lower_silver = np.array([0, 0, 192])
upper_silver = np.array([179, 25, 255])

# Variable to keep track of position of ball in frame
prevCircle = None
dist = lambda x1,y1,x2,y2: (x1-x2)**2-(y1-y2)**2

controlLoopTimes = [0] * 100
counter = 0;
start_time = time.time()
try:
    while True:
        # capture frame-by-frame
        # start_time = time.time()
        ret, frame = cap.read()

        # Convert the image from BGR to Grayscale color space
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use gaussian blue on grayscale image to smooth out noise
        blur = cv2.GaussianBlur(gray, (17,17), 0)

        # Detect circles using HoughCircles function
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 180, param1=100, param2=30, minRadius=13, maxRadius=75)

        # Draw best circle on the original image
        chosen = [320,0]
        if circles is not None:
            circles = np.uint16(np.around(circles))
            chosen = None
            for i in circles[0, :]:
                if chosen is None: chosen = i
                if prevCircle is not None:
                    if dist(chosen[0],chosen[1],prevCircle[0],prevCircle[1]) <= dist(i[0],i[1],prevCircle[0],prevCircle[1]):
                        chosen = i
            cv2.circle(frame, (chosen[0],chosen[1]), 1, (0,100,100), 3)
            cv2.circle(frame, (chosen[0],chosen[1]), chosen[2], (255,0,255), 3)
            prevCircle = chosen
        cv2.line(frame, (320,0),(320,640),(0,100,100),3)
        cv2.line(frame, (0,200),(320,640),(0,100,100),3)

        # current position of ball
        position = chosen[0]
        
        # Compute error
        error = setpoint - position

        # Compute PID output
        output = pid(error)

        # Map output to PWM signal
        duty_cycle = error/1000 # Convert to percentage
        if (np.absolute(duty_cycle) < 50 ):
            if(duty_cycle<0):
                duty_cycle = -duty_cycle
                GPIO.output(DIR,CCW)
            elif(duty_cycle>0):
                GPIO.output(DIR,CW)     
            pi_pwm.ChangeDutyCycle(duty_cycle)

        # display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        delta = time.time() - start_time
        start_time = time.time()
        controlLoopTimes.insert(0,delta)
        controlLoopTimes.pop()
        counter+=1
        if(counter%100==0):
            print("Average: " + str(np.mean(controlLoopTimes)) + 
                  " s. Maximum: " + str(max(controlLoopTimes)) + 
                  " s. Minimum: " + str(min(controlLoopTimes)) + "s")

        

    # release the capture
    cap.release()
    cv2.destroyAllWindows()

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    GPIO.cleanup()

