import os
import eel

from engine.features import *
from engine.command import *
from engine.auth import recoganize
def start():
    
    eel.init("www")

    playAssistantSound()
    @eel.expose
    def init():
        subprocess.call([r'device.bat'])
        eel.hideLoader()
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Successful")
            eel.hideFaceAuthSuccess()
            speak("Hello, Welcome Sir, How can i Help You")
            eel.hideStart()
            playAssistantSound()
        else:
            speak("Face Authentication Fail")
    os.system('start chrome.exe --app="http://localhost:8001/index.html"')

    @eel.expose
    def processTextInput(text):
        print(f"Received text input: {text}")
        # Add logic to process the text input here
        speak(f"You entered: {text}")

    eel.start('index.html', mode=None, host='localhost', port=8001, block=True)