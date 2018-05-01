#!/usr/bin/env python3
import pyaudio
import wave
import numpy as np
import time
import sys
import socket
import argparse

CHUNK = 512
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 1
RATE = 44100 #sample rate
RECORD_SECONDS = 5

parser = argparse.ArgumentParser()

#Takes in the arguments and assigns proper values that correspond to the flags, defaults are included
parser.add_argument("-s", "--server_ip", dest = "serverIP", default = "192.168.0.8", help = "Server IP")
parser.add_argument("-p", "--server_port", dest = "serverPort", default = "8888", help = "Server Port")
parser.add_argument("-z", "--socket_size", dest = "socketSize", default = "4096", help = "Socket Size")

args = parser.parse_args()



#This assigns the arguments to the corresponding 
IP = args.serverIP
PORT = int(args.serverPort)
SIZE = int(args.socketSize)

def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, dtype=np.int16)
    peak=np.average(np.abs(data))*2
    if peak > 10000:
        print(peak)
        return (data, pyaudio.paComplete)
    return (data, pyaudio.paContinue)
    
#####
#This section creates the socket, connection, and sends the data
#####
#create the socket and connect
try:
    #Create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except (socket.error, msg):
    print("Failed to create socket. Error Code: ", str(msg[0]), ", Error message: ", msg[1])
    sys.exit()
        
print("[Checkpoint] Socket Created")
        
try:
    #This connects to the server
    s.connect((IP, PORT))
    print("[Checkpoint] Connecting to " + IP + " on port " + repr(PORT))

except:
    print("Failed to connect to the server")
    sys.exit()
    
while True:
    
    p = pyaudio.PyAudio()
    
    
    
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
    
    
    print("* done recording")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    
    start = str.encode("start")
    s.sendall(start)
    print("Race started")
    
    dataBack = s.recv(SIZE)
    
    responseBack = bytes.decode(dataBack)
    if "Done" in responseBack:
        print("Race has finished")
        #s.close();
    elif "Finished" in responseBack:
        print("Meet has finished")
        break
    else:
        print("Unknown response")
        break

s.close()
