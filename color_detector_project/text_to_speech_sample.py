# run the following command to install:
# pip install pyttsx3
# see this site if you have problems: https://pypi.org/project/pyttsx3/

import pyttsx3
engine = pyttsx3.init()
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        # printing current voice rate
engine.setProperty('rate', 115)     # setting up new voice rate
voices = engine.getProperty('voices')       # getting details of current voice
engine.setProperty('voice', voices[0].id)  # changing index, changes voices. o for male
# engine.setProperty('voice', voices[1].id)   # changing index, changes voices. 1 for female
engine.say("This appears to be blue")
engine.say("Please reposition the clothing")
engine.runAndWait()
