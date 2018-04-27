import argparse

parser = argparse.ArgumentParser()

#Takes in the arguments and assigns proper values that correspond to the flags, defaults are included
parser.add_argument("-t", "--timer_ip", dest = "serverIP", default = "192.168.0.8", help = "Timer IP")
parser.add_argument("-d", "--debug", dest = "serverPort", default = "0", help = "Debug Mode")

args = parser.parse_args()
#Will be used for the server code 

#Section to listen for a signal from signal pi

#Loop to listen for rfid reads
# Might need a timer from threading

#After Loop send message to database with appropriate times

#Continue loop until there are no more races
