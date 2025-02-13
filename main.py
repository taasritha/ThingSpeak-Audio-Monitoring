import pyaudio
import numpy as np
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY") # Thingspeak API Key

url = f"https://api.thingspeak.com/update?api_key={API_KEY}"

#Audio recording parameters
FORMAT = pyaudio.paInt16   #16-bit audio format
CHANNELS = 1               #Mono channel
RATE = 44100               #Sample rate
CHUNK = 1024               #Number of audio frames per buffer

p = pyaudio.PyAudio()

def calculate_volume(data):
    audio_data = np.frombuffer(data, dtype=np.int16)
    rms = np.sqrt(np.mean(np.square(audio_data)))
    return rms

start_recording = input("Do you want to start recording audio? (Y/n): ").strip().lower()

if start_recording == 'y':
    print("Starting audio recording...")
    #starting the audio stream
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, frames_per_buffer=CHUNK)  
    try:
        while True:
            #reads a chunk of audio data from the microphone
            data = stream.read(CHUNK)
            
            volume = calculate_volume(data) #RMS value calculated
            
            normalized_volume = min(volume / 1000, 100)

            #Send the sound level data to ThingSpeak
            response = requests.get(url + f"&field1={normalized_volume}")
            
            if response.status_code == 200:
                print(f"Volume: {normalized_volume} - Sent to ThingSpeak")
            else:
                print("Failed to send data")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Recording stopped")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
else:
    print("Recording not started.")
