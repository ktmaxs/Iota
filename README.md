# Team IOTA

**COLOR DETECTOR**

IMPORTANT: Use Python 3.7 and pip3

Use the link below to set up venv and cv2  (Step 1 is not necessary)

https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/

Then, within the venv, 

`pip3 install webcolors`  documentation: https://webcolors.readthedocs.io/en/1.11.1/

`pip3 install pyttsx3` documentation: https://pypi.org/project/pyttsx3/

I recall having some problems with GPIO in the venv, but off the top of my head I can't remember.  You can google, and it you can't figure it out from there, email me *kmaxson18@georgefox.edu* and I can do my best to help

pygame should be already installed, but if you messed up like I did, you can just use this: https://amiradata.com/how-to-install-pygame-using-pip-ide/ 

`pip3 install -U scikit-learn` documentation: https://scikit-learn.org/stable/install.html


**BASKETBALL**


*Basketball Sensor:*

Link for project that was adpated: https://learn.adafruit.com/neopixel-mini-basketball-hoop/adding-a-point-sensor

Fun things to note about the wiring of the GemmaM0:
- The IR LEDs I purchased have the anode and cathode switched, so make sure you look very closely at the datasheet if you decide to use them
- The JST connectors I purchased also are switched, if you look at the GemmaM0 positive and negative are marked and DO NOT correspond with the JST connector
  - I had a hard time finding the correct JST connectors that worked well for the GemmaM0, the one that is currently connected barely fits (good luck trying to get it out if you ever have to)

Another thing to note: We were thinking the best way to use the sensor with a basketball hoop in order to remove the possibility of the netting interfering with the sensor, not sure if this is the best way to do it but definitely something to think about.


*Pi setup*
