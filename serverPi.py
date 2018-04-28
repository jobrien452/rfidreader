import argparse
import socket
import usb.core
import usb.util
import sys
sys.path.append('RfidFiles')
import reader
import time

from raceOrder import raceOrder

import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


parser = argparse.ArgumentParser()

#Takes in the arguments and assigns proper values that correspond to the flags, defaults are included
#parser.add_argument("-t", "--timer_ip", dest = "serverIP", default = "192.168.0.8", help = "Timer IP")
parser.add_argument("-d", "--debug", dest = "debug", default = "0", help = "Debug Mode")

args = parser.parse_args()

device = list(usb.core.find(find_all=True, idVendor=0xffff, idProduct = 0x0035))
reader1 = reader.Reader(0x16c0, 0x0035, 36, 3, should_reset=False)

def readReader1():
    reader1.initialize(device[0])
    global code1
    code1 = reader1.read()
    if code1 != '': 
        code1 = int(code1)
    reader1.disconnect()
    return code1

#Check if to enter debug mode
#Just tests the rfid reader
if args.debug != "0":
    print("In debug mode, Check RFID tags now")
    print("Press ctrl-C to end the debug mode")
    code1 = ""
    #Continuously checks for read values
    while True:
        code1 = readReader1()
        if code1 != "":
            print("From Read1: " + str(code1))
            code1 = ""        

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

#Setup db writes
client = boto3.resource('dynamodb', 
                        aws_access_key_id='AKIAIIOO6CX7UFZIVIEA',
                        aws_secret_access_key='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',
                        region_name='us-east-2')
table = client.Table('runtime2')
pe = "id, event, runtime, lane, rname"


#Global Params
IP = args.serverIP
HOST = ""
PORT = int(8888)
SIZE = int(4096)


#Section to listen for a signal from signal pi
#Tries to make a socket
try:
    #Create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except (socket.error, msg):
    print("Failed to create socket. Error Code: ", str(msg[0]), ", Error message: ", msg[1])
    sys.exit()

#Bind to timerPi
#bind the socket
try:
	s.bind((HOST, PORT))
except socket.error:
	print("Bind failed. Could not make port. Exiting program" )
	sys.exit()

print("Created socket at "+ socket.gethostbyname(socket.gethostname())+" on port "+ str(PORT))

s.listen(SIZE)

#Receive the data
def raceLoop(conn):
    #Keeps track of the race number
    raceCount = 0
    #Inf Loop to continue to listen for start signals
    while True:
        currRace = raceOrder[raceCount]
        currRaceDistInt = int(currRace.split()[1])
        #Should block here and only gets the start signal
        dataBack = conn.recv(SIZE)
        signalBack = bytes.decode(dataBack)
        s#ignalBack = "start"
        if "start" in signalBack:
            startTime = time.time()
            print("Race started: " + currRace)
            #Dictionary mapping rfid tag num to lane (key is the rfid num, value is list [lane number, num of laps, end time]
            rfidLaneMap = {64:[1,0,0],67:[2,0,0],65:[3,0,0],11:[4,0,0],68:[5,0,0]}
            #Gets the number of laps
            NumOLaps = int(currRaceDistInt/400)
            
            #Start listening for rfid tags
            laneFinishes = 0
            while laneFinishes < 5:
                code = readReader1()
                if code in rfidLaneMap:
                    rfidLaneMap[code][1] += 1
                    print("Runner in Lane: " + str(rfidLaneMap[code][0]) + " just scanned in")
                    if rfidLaneMap[code][0] >= NumOLaps:
                            print("Runner in Lane: " + str(rfidLaneMap[code][0]) + " just finished")
                            rfidLaneMap[code][2] = time.time()
                            laneFinishes += 1
                    code = ""
            #Print results
            for x in rfidLaneMap:
                #format race time
                raceTime = rfidLaneMap[x][2]-startTime
                strRaceTime = time.strftime("%H:%M:%S",time.gmtime(raceTime))
                print("Runner in Lane " + str(rfidLaneMap[x][0]) + " finshed with: " + strRaceTime)
                
                #Update time to database
                response = table.update_item(
                    Key={
                         'id':(rfidLaneMap[x][0]+(raceCount*5)),
                         'event':currRace
                    },
                    UpdateExpression="set runtime = :r",
                    ExpressionAttributeValues={
                        ':r': str(strRaceTime)
                    },
                    #ReturnValues="UPDATED_NEW"
                )
            
            
            #Send signal back to timer saying race is done
            sendBack = str.encode("Done")
            conn.sendall(sendBack)
            
            #Records number of races
            raceCount += 1
        else:
            print("There was a bad start signal")
            #sys.exit()
        

#Loop to listen for rfid reads
while 1:
    print("Listening for client connections")
    #Wait to accept a connection
    conn, addr = s.accept()
    #conn = ""
    #display client info
    print("Accepted client connection from "+ addr[0]+ " on port "+ str(addr[1]))
    
    #Begin waiting for a new race
    raceLoop(conn)
s.close()
