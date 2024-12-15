#code is from https://www.electronicwings.com/raspberry-pi/gps-module-interfacing-with-raspberry-pi changed to fit the test

import serial               #import serial pacakge
import time
import RPi.GPIO as GPIO
import threading
import sys                  #import system package
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub


def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    latitude_direction = NMEA_buff[2]           #extract latitude direction N/S from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    longtitude_direction = NMEA_buff[4]         #extract longitude direction E/W from GPGGA string
    
    print("NMEA Time: ", nmea_time,'\n')
    print ("NMEA Latitude:", nmea_latitude," ",latitude_direction," NMEA Longitude:", nmea_longitude," ",latitude_direction,'\n')
    
    if nmea_latitude == "":
        nmea_latitude = "0.0"
    
    if nmea_longitude == "":
        nmea_longitude = "0.0"

    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation

    if latitude_direction == 'S':
        lat = lat * -1

    if longtitude_direction == 'W':
        longi = longi * -1
    
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format

    
#convert raw NMEA string into degree decimal format   
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.7f" %(position)
    return position

class MyListener(SubscribeCallback):        # Not need for working of this program
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            pubnub.publish().channel(channel).message({'fieldA': 'awesome', 'fieldB': 10}).sync()
 
    def message(self, pubnub, message):
        print(message)
 
    def presence(self, pubnub, presence):
        pass    

pnconf = PNConfiguration()                                              # create pubnub_configuration_object
 
pnconf.publish_key = 'pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76'       # set pubnub publish_key
pnconf.subscribe_key = 'sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64'     # set pubnub subscibe_key
pnconf.uuid = "Petpi"                            

pubnub = PubNub(pnconf)                     # create pubnub_object using pubnub_configuration_object
my_listener = SubscribeListener()                   # create listner_object to read the msg from the Broker/Server
pubnub.add_listener(my_listener)

channel='GPS-Petpi' 

petID = "6728de4cb69cfe313c2fcb63"

message = {                                    # data to be published
    'username': 'Akshay: ps_01',
    'message' : 'This is my 1st msg... '
}

pubnub.subscribe().channels(channel).execute()

#pubnub.publish().channel(channel).message(message).sync()

buz_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buz_pin,GPIO.OUT)

led_pin = 22 

# Set up the LED GPIO
GPIO.setup(led_pin, GPIO.OUT)

gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyAMA0")              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0


def gps_tracker():
    global NMEA_buff  # Ensure you're using the global variable
    
    while True:
        try:
            received_data = (str)(ser.readline())  # Read NMEA string received
            GPGGA_data_available = received_data.find(gpgga_info)  # Check for NMEA GPGGA string
            if GPGGA_data_available > 0:
                GPGGA_buffer = received_data.split("$GPGGA,", 1)[1]  # Store data after "$GPGGA,"
                NMEA_buff = GPGGA_buffer.split(',')  # Store comma-separated data in buffer

                if isinstance(NMEA_buff, list) and len(NMEA_buff) >= 5:  # Ensure buffer is valid
                    GPS_Info()  # Get time, latitude, longitude
                    data = f"PetId = {petID}, lat: {lat_in_degrees}, long: {long_in_degrees}"
                    
                    GPIO.output(led_pin, True)
                    
                    try:
                        envelope = pubnub.publish().channel(channel).message({"data": data}).sync()
                        print("Published:", data)
                    except PubNubException as e:
                        print("Publishing error:", e)
                else:
                    print("Invalid NMEA buffer:", NMEA_buff)

                    # Turn off the LED for invalid data
                    GPIO.output(led_pin, False)

            else:
                # Turn off the LED if no valid GPGGA data is found
                GPIO.output(led_pin, False)

        except Exception as e:
            print("Error in gps_tracker:", e)

            # Turn off the LED in case of an error
            GPIO.output(led_pin, False)

        time.sleep(0.1)

def buzzer_handler():
    while True:
        result = my_listener.wait_for_message_on(channel)  # Read the new message on the channel
        print(result.message)                              # Print the new message
        
        # Check if the message string is in the format {"message":"ON"}
        message = result.message.strip()  # Remove leading/trailing whitespace
        
        if message.startswith('{"message":"') and message.endswith('"}'):
            # Extract the value of "message"
            value = message[len('{"message":"'):-len('"}')]
            
            if value == "ON":
                for i in range(3000):
                    GPIO.output(buz_pin, True)
                    time.sleep(0.001)
                    GPIO.output(buz_pin, False)
                    time.sleep(0.001)
            else:
                print("Message received, no action.")
        else:
            print("Invalid message format:", message)


if __name__ == "__main__":
    gps_thread = threading.Thread(target=gps_tracker)
    buzzer_thread = threading.Thread(target=buzzer_handler)

    # Set threads as daemon so they terminate when the main program exits
    gps_thread.daemon = True
    buzzer_thread.daemon = True

    gps_thread.start()
    buzzer_thread.start()

    # Keep the main program running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
        # Unsubscribe from the channel and stop PubNub instance
        pubnub.unsubscribe().channels(channel).execute()
        pubnub.stop()
        sys.exit(0)
