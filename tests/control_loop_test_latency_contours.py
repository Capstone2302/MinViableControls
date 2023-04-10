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
setpoint = 120/2  # Replace with your desired position

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
prevPosition = setpoint
speed = 0
dist = lambda x1,y1,x2,y2: (x1-x2)**2-(y1-y2)**2
def errorFunc(x,x_dot):
    return 1.25*gain(x)+0.02*x_dot

def gain(x):
    if(x<-10):
        return -1*(1/32*x**2-3/8*x+25/8)
    if(x<0):
        return x
    if(x<10):
        return x
    return 1/32*x**2+3/8*x+25/8

controlLoopTimes = [0] * 1000
positionLog = [0] * 1000
errorsLog = [0] * 1000
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

        blurred = cv2.GaussianBlur(frame, (3, 3), 0)

        # hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        colorMask = cv2.inRange(frame, lower_ball, upper_ball)
        # colorMask = cv2.erode(colorMask, None, iterations=2)
        # colorMask = cv2.dilate(colorMask, None, iterations=2)

        cnts = cv2.findContours(colorMask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M['m00'] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            else:
                center = (int(setpoint), int(120))

            # To see the centroid clearly
            if radius > 3:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 5)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # current position of ball
        try:
            delta = time.time() - start_time
            prevPosition = position
            position = center[0]
            speed = (prevPosition - position) / delta
        except:
            position = setpoint
            speed = 0 
        
        # Compute error
        error = setpoint - position

        # Compute PID output  
        # output = pid(error)

        # Map output to PWM signal
        duty_cycle = errorFunc(error, speed)
        # if (np.absolute(duty_cycle) > 99 ): # stop code if motor maxes out to prevent damage
        #     print("Max motor speed hit")
        #     break

        if(duty_cycle<0):
            duty_cycle = -duty_cycle
            GPIO.output(DIR,CCW)
        elif(duty_cycle>0):
            GPIO.output(DIR,CW)
        if(duty_cycle>100):
            duty_cycle=100
        pi_pwm.ChangeDutyCycle(duty_cycle)

        # display the resulting frame
        cv2.line(frame,(int(setpoint),0),(int(setpoint),240), (255,0,0),5)
        cv2.imshow('Frame', frame)
        cv2.imshow('Color mask', colorMask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        
        start_time = time.time()
        controlLoopTimes.insert(0,delta)
        controlLoopTimes.pop()
        positionLog.insert(0,position)
        positionLog.pop()
        
        errorsLog.insert(0,errorFunc(error, speed))
        errorsLog.pop()
        counter+=1
        if(counter%1000==0):
            print("Average: " + str(np.mean(controlLoopTimes)) + 
                " s. Maximum: " + str(max(controlLoopTimes)) + 
                " s. Minimum: " + str(min(controlLoopTimes)) + "s"
                + " Pwm: " + str(duty_cycle) + "Error: " + str(error))
            with open('/home/pi/Documents/WheelLogs/PositionLogs/PositionLog' + str(time.time_ns()) + '.txt', 'w') as tfile:
                tfile.write('Position' + 'n')
                tfile.write('\n'.join(str(x) for x in positionLog))
            with open('/home/pi/Documents/WheelLogs/ErrorLogs/ErrorLog' + str(time.time_ns()) + '.txt', 'w') as tfile:
                tfile.write('Error' + 'n')
                tfile.write('\n'.join(str(x) for x in errorsLog))
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

