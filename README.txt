Curerntly need the following packages:
	- pyusb (pip3 install pyusb)
	- Used for reading data from RFID reader
    -pyaudio: sudo apt-get install python3-pyaudio (used for the audio control)
    -do the section at the top of the page on https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/updating-alsa-config (for audio)
    -boto3 (pip3 install boto3) (used for dynamo db access)
    -flask
    
    Files and usage:
    dbSetup.py: resets the table to times of 00:00.00 to prepare the database
                command: python3 dbSetup.py
                
    serverPi.py: handles the timer and database interaction (reads in RFID tags and sends results to the AWS dynamo db table)
                 It communicates with the start pi to tell it when to start recording time for a race to start and handles how
                 many times runners should be passing the RFID scanner. It starts a timer when the starter pi tells it it started
                 command: sudo python3 server.py [-d]
                 If -d 1 can be added to the command which puts the system in debug mode which lets you test the RFID reader
                 
    raceOrder.py: holds an array that holds race orders used for the database
    
    webServer.py: It handles the interaction between the dynamo DB database and the flask server. It hosts the templates that
                  show the data reperesentation (in our case index.html). 
                  command: ./webServer.py
                  
    starter.py: This is the starter Pi. It connects to the timer pi (server.py) via sockets and then waits for a race to start.
                A mic is used to register sound and if it is above the threshold it "starts" the race by sending a messeage to the timer pi.
                The threshold registers at about the sound of a clap. It then waits until the timer pi returns a message. If the timer says the race is done then it
                starts the next race. If it is told the meet is finished then it ends the connection. 
                command: python3 starter.py -s IP_ADDRESS -p PORT -z SOCKET_SIZE
                the arguments have default values
                  
    Inside templates folder: index.html: The template for the table on the flask server
    
    Inside static folder: style.css: This is the style for the template
    
    Inside RFIDFiles folder: Used to read in RFID tags. Code found from online that is used on the backend to make the RFID parts of the server pi work
    
    