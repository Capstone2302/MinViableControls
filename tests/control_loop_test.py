import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')

from pid import PID
# Set up GPIO for PWM output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)  # 50 Hz PWM frequency
pwm.start(0)  # Start with 0% duty cycle

# Define PID parameters
kp = 0.1
ki = 0.01
kd = 0.05

# Set desired position
setpoint = 0  # Replace with your desired position

# Initialize PID controller
pid = PID(kp, ki, kd, setpoint)

# initialize camera
cap = cv2.VideoCapture(0)

# define range of blue color in HSV
lower_blue = np.array([110,50,50])
upper_blue = np.array([130,255,255])

while True:
    # capture frame-by-frame
    ret, frame = cap.read()

    # convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # find contours in the thresholded image
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # iterate through each contour and compute the bounding box
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    
    # current position of ball
    position = -5 #TODO: Save position of ball from cv2 contours
    
    # Compute error
    error = setpoint - position

    # Compute PID output
    output = pid(error)

    # Map output to PWM signal
    duty_cycle = output * 100  # Convert to percentage
    pwm.ChangeDutyCycle(duty_cycle)

    # Wait for a short period of time before updating again
    time.sleep(0.01)

    # display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the capture
cap.release()
cv2.destroyAllWindows()