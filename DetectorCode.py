#Written by Bret Henkel during spring of 2021. Phone number (916)-844-5792, email bhenkel18@georgefox.edu
#Please reach out if you are working on this project and lost. A lot of the code was adapted from an online
#resource. Designed to run on RaspberryPi

#Import all necessary modules
import numpy as np
import cv2
import cv2.aruco as aruco
import sys, time, math
import pyttsx3
import pygame

#Initialize pygame
pygame.mixer.init()

#Set up the text to speech functionality
from espeak import espeak
from time import sleep

#Set the numbers for the aruco markers that the camera will look for
id_to_find = [10,26]
marker_size = 9.5 # cm


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6

# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    return np.array([x, y, z])


#Camera Calibration Path
#These files are required and have to be generated through a seperate program and are dependent on the camera used
#Store them at the location specified in calib_path (change this to match what you have)
calib_path = "/home/pi/.virtualenvs/cv/"
camera_matrix = np.loadtxt(calib_path+'camMTX.txt')
camera_distortion = np.loadtxt(calib_path+'distort.txt')

#Rotation matrix
R_flip = np.zeros((3,3),dtype=np.float32)
R_flip[0,0] = 1.0
R_flip[1,1] = 1.0
R_flip[2,2] = -1.0

#Load the Aruco marker dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters = aruco.DetectorParameters_create()

#Set up the video camera
cap = cv2.VideoCapture(0)
# Set camera size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

#Set the font for text on the screen
font = cv2.FONT_HERSHEY_PLAIN

#Loading tons which will indicate if the user is turned too far to the left or right, or the
#aruco marker is not within sight of the camera
right = pygame.mixer.Sound('/home/pi/.virtualenvs/cv/250.wav')
left = pygame.mixer.Sound('/home/pi/.virtualenvs/cv/440.wav')
outer = pygame.mixer.Sound('/home/pi/.virtualenvs/cv/100.wav')

#Initialize counter. The counter keeps track of how many frames the image has been undetected for
instanceCounter = 0

#Boolean values that keep track of the last direction that the marker was sighted in
rightB = False
leftB = False

#Starts playing the out of view sound infinitely
outer.play(loops=-1)

#Set the volume of the sounds
pygame.mixer.Sound.set_volume(outer,0.5)

#Initialize counter. The counter will govern when the program will read out the distance and
#orientation angle after the user is looking straight on the target (+/- 1°)
centeredCount = 0

#Orientation is the least accurate reading, especially as the orientation approaches 0 degrees
#To help compensated the average of a series of last readings is taken. Here the array is constructed
orientationArray = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12])
sortedOrientationArray = np.array([])

#The main loop
while True:
    #Get a camera frame
    ret, frame = cap.read()

    #Turn the image into grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #Run the detection algorithm
    corners, ids, rejected = aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters,
                                                 cameraMatrix=camera_matrix,distCoeff=camera_distortion)

    instanceCounter+=1
    if instanceCounter>20:
        #The marker has not been detected for too long
        pygame.mixer.Sound.stop(right)
        pygame.mixer.Sound.stop(left)
        outer.play(loops=-1)
        pygame.mixer.Sound.set_volume(outer,0.5)
    if isinstance(ids, np.ndarray) and ids[0] in id_to_find:
        #Marker was detected
        instanceCounter = 0

        #Gathers location data from Aruco algorithm
        ret = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)
        rvec, tvec = ret[0][0,0,:], ret[1][0,0,:]

        #These functions are useful if using a live feed
        #aruco.drawDetectedMarkers(frame,corners)
        #aruco.drawAxis(frame, camera_matrix, camera_distortion, rvec, tvec, 10)

        #Adjustment of the distance reading based off of unit conversions and some calibration
        z = tvec[2] * 0.3 + 0.2588
        x = tvec[0] * 0.3695

        #The distance and position angle are calculated
        dist = round(math.sqrt(pow(z, 2) + pow(x, 2)), 0)
        pos_angle = int(math.degrees(math.atan(x / z)))+8

        #Adjust the arrays mathematically
        R_ct = np.matrix(cv2.Rodrigues(rvec)[0])
        R_tc = R_ct.T

        # -- Get the attitude in terms of euler 321 (Needs to be flipped first)
        #The following code is a rather inefficient way to find an average of the last readings from the
        #marker for the orientation angle while also removing outliers
        roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(R_flip * R_tc)
        orien_angle_inst = int(math.degrees(-1*pitch_marker))
        orien_angle = 0
        orientationArray = np.delete(orientationArray,0,0)
        orientationArray = np.append(orientationArray,orien_angle_inst)
        sorted_orientation_array = np.copy(orientationArray)
        sorted_orientation_array.sort()
        sorted_orientation_array = sorted_orientation_array[2:-2]
        mean = np.mean(sorted_orientation_array)
        std = np.std(sorted_orientation_array)
        distance_from_mean = abs(sorted_orientation_array - mean)
        max_dev = 1
        not_outlier = distance_from_mean < max_dev * std
        no_outliers = sorted_orientation_array[not_outlier]
        orien_angle = int(sorted_orientation_array.mean())

        #Chooses which tone to play
        if pos_angle > 0:
            tone = 6000
        else:
            tone = 4000

        #Change the feet and inches
        feet=int(dist//12)
        inchesLeft=int(dist%12)
        if inchesLeft>=3 and inchesLeft<=9:
            half="and a half "
        elif inchesLeft>9:
            feet+=1
            half=""
        else:
            half=""

        #If the camera has been aimed at the marker for 10 frames the distance and orientation
        #angle are read out
        if centeredCount>10:
            phrase = 'Distance {feet} {half} feet'.format(feet=feet, pos_angle=pos_angle, orien_angle=orien_angle, half=half)
            espeak.set_voice('english')
            espeak.synth(phrase)
            while espeak.is_playing():
                #espeak is asynchronous, so wait politely until it's finished
                sleep(0.01)
            phrase = 'Orientation {orien_angle} degrees'.format(dist=dist, pos_angle=pos_angle, orien_angle=-orien_angle)
            espeak.set_voice('english')
            espeak.synth(phrase)
            while espeak.is_playing():
                #espeak is asynchronous, so wait politely until it's finished
                sleep(0.01)
            centeredCount=0

        #Adjust the tones playing depending on the circumstance that the marker is in
        #Volume decreases as the marker approaches the center of the camera view
        if pos_angle < 1 and pos_angle > -1:
            pygame.mixer.Sound.stop(left)
            pygame.mixer.Sound.stop(right)
            pygame.mixer.Sound.stop(outer)
            centeredCount+=1
        elif pos_angle < 0:
            left.play(loops=-1)
            pygame.mixer.Sound.set_volume(left, -1*pos_angle/30)
            pygame.mixer.Sound.stop(right)
            rightB = False
            leftB = True
            outer.stop()
            centeredCount=0
        elif pos_angle > 0:
            right.play(loops=-1)
            pygame.mixer.Sound.set_volume(right, pos_angle/30)
            pygame.mixer.Sound.stop(left)
            rightB = True
            leftB = False
            outer.stop()
            centeredCount=0
    #controls exiting? May be an artifact from an old version of the code
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        break