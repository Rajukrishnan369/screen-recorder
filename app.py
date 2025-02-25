from flask import Flask, render_template, request, jsonify
import threading
import cv2
import numpy as np
import pyautogui
import sounddevice as sd
import wave
import queue
import os

app = Flask(__name__)

# Global variables
recording = False
video_filename = "recorded_screen.avi"
audio_filename = "recorded_audio.wav"
output_filename = "final_output.mp4"
audio_queue = queue.Queue()

# Screen Recording Function
def record_screen():
    global recording
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_filename, fourcc, 10.0, screen_size)
    
    while recording:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
    
    out.release()

# Audio Recording Function
def record_audio():
    global recording
    samplerate = 44100
    channels = 2
    with wave.open(audio_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        
        def callback(indata, frames, time, status):
            if status:
                print(status)
            audio_queue.put(indata.copy())
        
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            while recording:
                while not audio_queue.empty():
                    wf.writeframes(audio_queue.get())

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start_recording():
    global recording
    recording = True
    threading.Thread(target=record_screen).start()
    threading.Thread(target=record_audio).start()
    return jsonify({"message": "Recording started"})

@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording
    recording = False
    return jsonify({"message": "Recording stopped"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
