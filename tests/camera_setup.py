import pygame
import pygame.camera
from pygame.locals import *
import time

# initialize pygame
pygame.init()
pygame.camera.init()

# set the resolution of the camera
width = 640
height = 480

# create a new display surface
screen = pygame.display.set_mode((width, height))

# create a new camera instance
cam = pygame.camera.Camera("/dev/video0", (width, height))

# start the camera
cam.start()

# create a loop to capture and display images
while True:
    # capture an image
    image = cam.get_image()

    # draw the image on the screen
    screen.blit(image, (0, 0))
    pygame.display.update()

    # handle events
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # stop the loop if the user presses the ESC key
            cam.stop()
            pygame.quit()
            quit()