import webcolors
import time
# import random
import pyttsx3
import cv2

camera = cv2.VideoCapture(0)

start = time.time()

engine = pyttsx3.init()
engine.setProperty("rate", 115)
engine.setProperty("volume", 1)

engine.say("hello katie")


# status = random.randrange(3)
status = 0


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


def speak(color):
    if status == 0:
        print("here")
        engine.say("This item appears to be " + str(color))
    elif status == 1:
        engine.say("Please move closer")
    else:
        engine.say("Please move farther away")
    engine.runAndWait()
banana = 0

while banana < 200:
   # r = random.randrange(256)
   # g = random.randrange(256)
   # b = random.randrange(256)

    return_value, image = camera.read()

    r = image.item(320, 240, 2)
    g = image.item(320, 240, 1)
    b = image.item(320, 240, 0)
    requested_color = (r, g, b)
    submit_color = get_colour_name(requested_color)


    speak(submit_color[1])

    print(status)
    print(submit_color[1])
    print(str(r) + "," + str(g) + "," + str(b))
    # print("Actual colour name:", actual_name, ", closest colour name:", closest_name)
    # print("Tempo: ", time.time() - start)
    banana = banana + 1


camera.release()
cv2.destroyAllWindows()
del(camera)
