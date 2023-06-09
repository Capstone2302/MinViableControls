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
setpoint = 160  # Replace with your desired position

# Initialize PID controller
pid = PID(kp, ki, kd, setpoint)

# initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Define range of ball color in HSV format
lower_bgr = np.array([0,0,0])
upper_bgr = np.array([255,255,255])
lower_hsv = np.array([0,0,0])
upper_hsv = np.array([0,0,80])


# Variable to keep track of position of ball in frame
prevCircle = None
dist = lambda x1,y1,x2,y2: (x1-x2)**2-(y1-y2)**2

controlLoopTimes = [0] * 100
counter = 0;
start_time = time.time()

import picamera
import picamera.array

# Initialize the camera and the output array
camera = picamera.PiCamera()
camera.resolution = (340, 240)
rawCapture = picamera.array.PiRGBArray(camera, size=(340, 240))

# Allow the camera to warm up
time.sleep(2)

try:
    # Continuously capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
<<<<<<< Updated upstream:tests/control_loop_test_latency.py
        frame = frame.array
        # Convert the image from BGR to Grayscale color space
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use gaussian blue on grayscale image to smooth out noise
        blur = cv2.GaussianBlur(gray, (7,7), 0)

        # Detect circles using HoughCircles function
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 180, param1=100, param2=30, minRadius=6, maxRadius=30)

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
        cv2.line(frame, (160,0),(160,640),(0,100,100),3)
=======
        frame = frame.array[110:150,100:220,:]

        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        colorMask = cv2.inRange(hsvFrame, lower_hsv, upper_hsv)

        fgMask = backSub.apply(frame)
>>>>>>> Stashed changes:tests/control_loop_test_latency_backsub.py

        # current position of ball
        position = chosen[0]
        
        # Compute error
        error = setpoint - position

        # Compute PID output
        output = pid(error)

        # Map output to PWM signal
        duty_cycle = error/1000 # Convert to percentage
        if (np.absolute(duty_cycle) < 30 ):
            if(duty_cycle<0):
                duty_cycle = -duty_cycle
                GPIO.output(DIR,CCW)
            elif(duty_cycle>0):
                GPIO.output(DIR,CW)     
            pi_pwm.ChangeDutyCycle(duty_cycle)

        # display the resulting frame
        cv2.imshow('Frame', frame)
        cv2.imshow('FG Mask', fgMask)
        cv2.imshow('Color Mask', colorMask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        delta = time.time() - start_time
        start_time = time.time()
        controlLoopTimes.insert(0,delta)
        controlLoopTimes.pop()
        counter+=1
        if(counter%10==0):
            print("Average: " + str(np.mean(controlLoopTimes)) + 
                " s. Maximum: " + str(max(controlLoopTimes)) + 
                " s. Minimum: " + str(min(controlLoopTimes)) + "s"
                + " Pwm: " + str(duty_cycle))
            print( lower_hsv)
            print(upper_hsv)
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

