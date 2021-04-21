# Color Detector Code
# Authors: Kate Maxson and Bret Henkel
# Servant Team IOTA 2020-2021
# 
# contact: kmaxson18@georgefox.edu or 209.770.7262

# ======================================================
# IMPORTS
# ======================================================

import webcolors
import time
import pyttsx3
import cv2
import numpy as np
import RPi.GPIO as GPIO
import sys
import pygame
from sklearn.cluster import KMeans
start = time.time()


# ======================================================
# ACTUAL CODE
# ======================================================


# Set up I/O and tts engine
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # go button
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # turn off button
GPIO.setup(12, GPIO.OUT) # LED output
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # photoresistor input

engine = pyttsx3.init()
engine.setProperty("rate", 115)
engine.setProperty("volume", 1)


# Available edit: Create a way to tell how far away the item is
# this is a remnant of an idea to detect the distance from the object
#   and only allow an image to be taken and the colors to be read if the 
#   object was within a certain range
status = 0


# creates the histogram
def make_histogram(cluster):
    num_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    hist, _ = np.histogram(cluster.labels_, bins=num_labels)
    hist = hist.astype('float32')
    hist /= hist.sum()
    return hist


# prints bars with the height, width, and color recorded
def make_bar(height, width, color):
    bar = np.zeros((height, width, 3), np.uint8)
    bar[:] = color
    red, green, blue = int(color[2]), int(color[1]), int(color[0])
    hsv_bar = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv_bar[0][0]
    return bar, (red, green, blue), (hue, sat, val)


# sorts recorded values based on HSV values
def sort_hsvs(hsv_list):
    bars_with_indexes = []
    for index, hsv_val in enumerate(hsv_list):
        bars_with_indexes.append((index, hsv_val[0], hsv_val[1], hsv_val[2]))
    bars_with_indexes.sort(key=lambda elem: (elem[1], elem[2], elem[3]))
    return [item[0] for item in bars_with_indexes]


# locates the closest color to the inputted values to read out the color
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


# gets color name from closest color values (RGB)
def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


# this is where the status would come into play
def speak(color):
    # currently only this loop is needed
    if status == 0:
        print("here")
        engine.say("This item appears to be " + str(color))
    elif status == 1:
        engine.say("Please move closer")
    else:
        engine.say("Please move farther away")
    engine.runAndWait()


# begin loop
while True:
    # this button is connected to pin 8.  It ends the program
    if GPIO.input(8) == GPIO.HIGH:
        cv2.VideoCapture(-1).release()
        cv2.destroyAllWindows()
        sys.exit()
    # if the other button is pressed (attached to pin 10) do this
    if GPIO.input(10) == GPIO.HIGH:
        # record light input
        photoVal = GPIO.input(16)
        # get how bright the led should be set to 
        ledVal = (1023 - photoVal)
        # these lines had timing issues so they are commented out
        #engine.say("Three")
        #engine.say("Two")
        #engine.say("One")
        
        # delay
        cv2.waitKey(750)

        # check if value is above a certain point, then turn on the LED
        if (photoVal < 700):
            GPIO.output(12, ledVal)
        # otherwise, turn off LED
        else:
            GPIO.output(12, 0)

        # checks if the camera has been turned on yet, then sets it
        if cv2.VideoCapture(-1).isOpened() == False:
            camera = cv2.VideoCapture(-1)
        # otherwise, turn off the camera and set it again
        else:
            # print("already taken") # debug statement
            cv2.VideoCapture(-1).release()
            camera = cv2.VideoCapture(-1)

        # take the picture
        for i in range(1):
            return_value, imageggf = camera.read()
            cv2.imwrite('background_image.bmp', imageggf)
            bg = pygame.image.load("background_image.bmp")
        del camera
        # print(return_value) # debug statement
        cv2.imshow("image", imageggf)
        # creates enough delay that the camera has time to update view to show accurate image
        cv2.waitKey(500)

        # takes image
        img1 = cv2.imread('background_image.bmp')
        img = img1[80:400, 80:560]
        height, width, _ = np.shape(img)
        print(height, width)
        image = img.reshape((height * width, 3))

        # sets the number of clusters to get colors
        num_clusters = 3
        clusters = KMeans(n_clusters=num_clusters)
        clusters.fit(image)

        # creates the histograms for testing (remove these for the actual product because there will not be a screen attached, so it becomes unnecessary and can slow the whole thing down, same with the bars defined and drawn below)
        histogram = make_histogram(clusters)
        combined = zip(histogram, clusters.cluster_centers_)
        combined = sorted(combined, key=lambda x: x[0], reverse=True)

        bars = []
        hsv_values = []
        cols = []
        for index, rows in enumerate(combined):
            bar, rgb, hsv = make_bar(100, 100, rows[1])
            print(f'Bar {index + 1}')
            print(f'  RGB values: {rgb}')
            print(f'  HSV values: {hsv}')
            hsv_values.append(hsv)
            bars.append(bar)
            # splits into the colors
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            requested_color = (r, g, b)
            print(requested_color)
            submit_color = get_colour_name(requested_color)
            print(submit_color)
            speak(submit_color[1])
        sorted_bars_indexes = sort_hsvs(hsv_values)
        sorted_bars = [bars[idx] for idx in sorted_bars_indexes]
        cv2.imshow('Sorted by HSV values', np.hstack(sorted_bars))
        cv2.imshow(f'{num_clusters} Most Common Colors', np.hstack(bars))
        cv2.waitKey(500)
        # debugging space
        print()
        print()
        print()
        # turn off LED
        GPIO.output(12, 0)


camera.release()
cv2.destroyAllWindows()
del camera
