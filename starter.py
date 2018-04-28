#!/usr/bin/env python3
import pyaudio
import wave
import numpy as np
import time
import sys

CHUNK = 512
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 1
RATE = 44100 #sample rate
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, dtype=np.int16)
    peak=np.average(np.abs(data))*2
    if peak > 10000:
        print(peak)
        return (data, pyaudio.paComplete)
    return (data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input_device_index=2,
                input=True,
                frames_per_buffer=CHUNK, stream_callback=callback) #buffer

print("* recording")
stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

'''

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    #data = stream.read(CHUNK)
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    peak=np.average(np.abs(data))*2
    if peak > 10000:
        print(peak)
    #frames.append(data) # 2 bytes(16 bits) per channel
'''

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

