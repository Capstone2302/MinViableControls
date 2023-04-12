from __future__ import print_function
import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
import imutils
import sys

sys.path.append('/home/pi/.local/lib/python3.7/site-packages')

# Set up GPIO for PWM output
DIR = 6
PWM = 13
CW =1
CCW =0
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)

pi_pwm = GPIO.PWM(PWM,100)		#create PWM instance with frequency
pi_pwm.start(0)	


import picamera
import picamera.array

# Continuously capture frames from the camera
class Controller:
    lower_ball = np.array([25,20,10])
    upper_ball = np.array([80,65,50])
    setpoint = 120/2
    kp = 10
    ki = 0.1
    kd = 1

    def __init__(self):
        self.controlLoopTimes = [0] * 100
        self.positionLog = [0] * 100
        self.errorsLog = [0] * 100
        self.counter = 0
        self.camera = picamera.PiCamera()
        self.camera.resolution = (340, 240)
        self.rawCapture = picamera.array.PiRGBArray(self.camera, size=(340, 240))
        self.start_time = time.time()
        self.prevPosition = Controller.setpoint
        self.position = Controller.setpoint
        self.speed = 0
    def errorFunc(x,x_dot):
        return 0.75*Controller.gain(x)+0.02*x_dot

    def gain(x):
        # if(x<-10):
        #     return -1*(1/32*x**2-3/8*x+25/8)
        # if(x<0):
        #     return x
        # if(x<10):
        #     return x
        # return 1/32*x**2+3/8*x+25/8
        return x
    def control_routine(self):
        self.camera.capture(self.rawCapture, format='bgr', use_video_port=True)

        frame = self.rawCapture.array[110:150,100:220,:]

        blurred = cv2.GaussianBlur(frame, (3, 3), 0)

        # hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        colorMask = cv2.inRange(frame, Controller.lower_ball, Controller.upper_ball)
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
                center = (int(Controller.setpoint), int(120))

            # To see the centroid clearly
            if radius > 3:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 5)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # current position of ball
        try:
            delta = time.time() - self.start_time
            self.prevPosition = self.position
            self.position = center[0]
            speed = (self.prevPosition - self.position) / delta
        except:
            self.position = self.setpoint
            speed = 0 
            delta = 0
        
        # Compute error
        error = self.setpoint - self.position

        # Map output to PWM signal
        duty_cycle = Controller.errorFunc(error, speed)
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
        cv2.line(frame,(int(self.setpoint),0),(int(self.setpoint),240), (255,0,0),5)
        cv2.imshow('Frame', frame)
        cv2.imshow('Color mask', colorMask)
        cv2.waitKey(1)
        
        
        self.start_time = time.time()
        self.controlLoopTimes.insert(0,delta)
        self.controlLoopTimes.pop()
        self.positionLog.insert(0,self.position)
        self.positionLog.pop()
        
        self.errorsLog.insert(0,Controller.errorFunc(error, speed))
        self.errorsLog.pop()
        self.counter+=1
        if(self.counter%10==0):
            print("Average: " + str(np.mean(self.controlLoopTimes)) + 
                " s. Maximum: " + str(max(self.controlLoopTimes)) + 
                " s. Minimum: " + str(min(self.controlLoopTimes)) + "s"
                + " Pwm: " + str(duty_cycle) + "Error: " + str(error))
            with open('/home/pi/Documents/WheelLogs/PositionLogs/PositionLog' + str(time.time_ns()) + '.txt', 'w') as tfile:
                tfile.write('Position' + 'n')
                tfile.write('\n'.join(str(x) for x in self.positionLog))
            with open('/home/pi/Documents/WheelLogs/ErrorLogs/ErrorLog' + str(time.time_ns()) + '.txt', 'w') as tfile:
                tfile.write('Error' + 'n')
                tfile.write('\n'.join(str(x) for x in self.errorsLog))
        pass

        # Clear the output array for the next frame
        self.rawCapture.truncate()
        self.rawCapture.seek(0) 
