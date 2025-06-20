import os
import shlex
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
import pyttsx3
import speech_recognition as srN
from engine.command import speak
from engine.config import ASSISTANT_NAME
import pywhatkit as kit
import pvporcupine
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

# Initialize the TTS engine with a female voice
def set_female_voice():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Set a female voice (if available)
    for voice in voices:
        if "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine

engine = set_female_voice()

def speak(text):
    """Speak the given text using a female voice."""
    engine.say(text)
    engine.runAndWait()

def speak_and_type(text):
    """Speak the text and type it out."""
    speak(text)  # Speak the text
    time.sleep(1)  # Wait for the speech to start
    pyautogui.write(text, interval=0.1)  # Type the text

def listen_command():
    """Listen to the user's voice command and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio, language="en-US")  # Use Google Speech Recognition
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        speak("Sorry, there was an issue with the speech recognition service.")
        return None

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening " + query)
                os.startfile(results[0][0])

            elif len(results) == 0:
                cursor.execute(
                    'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()

                if len(results) != 0:
                    speak("Opening " + query)
                    webbrowser.open(results[0][0])
                else:
                    speak("Opening " + query)
                    try:
                        os.system('start ' + query)
                    except:
                        speak("Not found")
        except:
            speak("Something went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)

def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        # Pre-trained keywords
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)

        # Loop for streaming
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # Processing keyword from mic
            keyword_index = porcupine.process(keyword)

            # Check if keyword is detected
            if keyword_index >= 0:
                print("Hotword detected")
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('Contact does not exist')
        return 0, 0

def whatsApp(mobile_no, message, flag, name):
    if flag == 'message':
        jarvis_message = "Message sent successfully to " + name
    elif flag == 'call':
        message = ''
        jarvis_message = "Calling " + name
    else:
        message = ''
        jarvis_message = "Starting video call with " + name

    # Construct the WhatsApp URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={message}"
    print(f"WhatsApp URL: {whatsapp_url}")

    # Open WhatsApp with the constructed URL
    try:
        webbrowser.open(whatsapp_url)
        time.sleep(5)  # Wait for WhatsApp to open

        # Focus on the chat input field and send the message
        pyautogui.hotkey('enter')  # Send the message
        speak(jarvis_message)
    except Exception as e:
        speak("Sorry, I couldn't open WhatsApp.")
        print(f"Error: {e}")

def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path=r"engine\cookies.json")

    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_input)
    print(response)
    speak_and_type(response)  # Speak and type the response
    return response

def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak("Calling " + name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:' + mobileNo
    os.system(command)

def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("Sending message")  # Speak the action
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # Open SMS app
    tapEvents(136, 2220)
    # Start chat
    tapEvents(819, 2192)
    # Search mobile number
    adbInput(mobileNo)
    # Tap on name
    tapEvents(601, 574)
    # Tap on input
    tapEvents(390, 2270)
    # Type the message
    speak_and_type(message)  # Speak and type the message
    # Send
    tapEvents(957, 1397)
    speak("Message sent successfully to " + name)  # Speak the confirmation

def send_whatsapp_message():
    speak("Whom do you want to send the message to?")
    name = listen_command()
    if name:
        mobile_no, contact_name = findContact(name)
        if mobile_no:
            speak(f"What message do you want to send to {contact_name}?")
            message = listen_command()
            if message:
                whatsApp(mobile_no, message, "message", contact_name)

def open_link():
    speak("What link do you want to open?")
    link = listen_command()
    if link:
        speak(f"Opening {link}")
        webbrowser.open(link)

def handle_voice_commands():
    speak("How can I assist you?")
    command = listen_command()
    if command:
        if "send a message to" in command or "send message to" in command:
            # Extract the name from the command
            name = command.replace("send a message to", "").replace("send message to", "").strip()
            if name:
                mobile_no, contact_name = findContact(name)
                if mobile_no:
                    speak(f"What message do you want to send to {contact_name}?")
                    message = listen_command()
                    if message:
                        whatsApp(mobile_no, message, "message", contact_name)
                    else:
                        speak("No message provided.")
                else:
                    speak(f"Sorry, I couldn't find {name} in your contacts.")
            else:
                speak("Sorry, I didn't catch the name.")
        elif "open link" in command or "open website" in command:
            open_link()
        else:
            speak("Sorry, I don't understand that command.")

if __name__ == "__main__":
    while True:
        handle_voice_commands()