from __future__ import print_function
import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
import imutils
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

pi_pwm = GPIO.PWM(PWM,100)		#create PWM instance with frequency
pi_pwm.start(0)	

# Define PID parameters
kp = 10
ki = 0.1
kd = 1

# Set desired position
setpoint = 340/2  # Replace with your desired position

# Initialize PID controller
pid = PID(kp, ki, kd, setpoint)

# initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Define range of ball color in HSV format
lower_ball = np.array([25,20,10])
upper_ball = np.array([80,65,50])

# Variable to keep track of position of ball in frame
prevCircle = None
dist = lambda x1,y1,x2,y2: (x1-x2)**2-(y1-y2)**2

controlLoopTimes = [0] * 100
counter = 0
start_time = time.time()

import picamera
import picamera.array

# Initialize the camera and the output array
camera = picamera.PiCamera()
camera.resolution = (340, 240)
rawCapture = picamera.array.PiRGBArray(camera, size=(340, 240))

# Allow the camera to warm up
time.sleep(2)

backSub = cv2.createBackgroundSubtractorMOG2()

try:
    # Continuously capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        frame = frame.array[110:150,100:220,:]

        # hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        colorMask = cv2.inRange(frame, lower_ball, upper_ball)

        # fgMask = backSub.apply(frame)

        contours = cv2.findContours(colorMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours_img = 

        # contour_img = cv2.drawContours(colorMask.copy(), contours, -1, (0,255,0), 2)

        cnts = imutils.grab_contours(contours)

        if(len(cnts) > 0):
            c = max(cnts, key=cv2.contourArea)
            ((x,y),radius) = cv2.minEnclosingCircle(c)


            # Compute moments of contour
            M = cv2.moments(c)

            # Compute x, y coordinates of centroid
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(colorMask, (int(x),int(y)), int(radius), (0, 255,255), 2)
            else:
                cX, cY = setpoint, 0

        # current position of ball
        try:
            position = cX
        except:
            position = setpoint
        
        # Compute error
        error = setpoint - position

        # Compute PID output  
        output = pid(error)

        # Map output to PWM signal
        duty_cycle = error/100 # Convert to percentage
        if (np.absolute(duty_cycle) > 30 ): #check if we are not going at full speed
            break

        if(duty_cycle<0):
            duty_cycle = -duty_cycle
            GPIO.output(DIR,CCW)
        elif(duty_cycle>0):
            GPIO.output(DIR,CW)     
        pi_pwm.ChangeDutyCycle(duty_cycle)

        # display the resulting frame
        # cv2.imshow('Frame', frame)
        # cv2.imshow('FG Mask', fgMask)
        cv2.line(colorMask,(int(setpoint),0),(int(setpoint),240), (255,0,0),5)
        cv2.imshow('Color mask', colorMask)
        # cv2.imshow('Contour mask', contour_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        delta = time.time() - start_time
        start_time = time.time()
        controlLoopTimes.insert(0,delta)
        controlLoopTimes.pop()
        counter+=1
        if(counter%100==0):
            print("Average: " + str(np.mean(controlLoopTimes)) + 
                # " s. Maximum: " + str(max(controlLoopTimes)) + 
                # " s. Minimum: " + str(min(controlLoopTimes)) + "s"
                 " Pwm: " + str(duty_cycle) + "Error: " + str(error))
        pass
    
        # Clear the output array for the next frame
        rawCapture.truncate()
        rawCapture.seek(0)

    # release the capture
    cap.release()
    cv2.destroyAllWindows()

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    GPIO.cleanup()
