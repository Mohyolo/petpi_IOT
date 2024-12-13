#code is from https://www.electronicwings.com/raspberry-pi/gps-module-interfacing-with-raspberry-pi changed to fit the test

import serial               #import serial pacakge
import time
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
    
pnconf = PNConfiguration()                                              # create pubnub_configuration_object
 
pnconf.publish_key = 'pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76'       # set pubnub publish_key
pnconf.subscribe_key = 'sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64'     # set pubnub subscibe_key
pnconf.uuid = "Petpi"                            

pubnub = PubNub(pnconf)                     # create pubnub_object using pubnub_configuration_object

channel='GPS-Petpi' 

petID = "6728de4cb69cfe313c2fcb63"

message = {                                    # data to be published
    'username': 'Akshay: ps_01',
    'message' : 'This is my 1st msg... '
}

pubnub.subscribe().channels(channel).execute()

#pubnub.publish().channel(channel).message(message).sync()

gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyAMA0")              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0

try:
    while True:
        received_data = (str)(ser.readline())                   #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                 
        if (GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
            NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
            GPS_Info()                                          #get time, latitude, longitude
            print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
            map_link = 'http://maps.google.com/?q=' + lat_in_degrees + ',' + long_in_degrees    #create link to plot location on Google map
            print("<<<<<<<<press ctrl+c to plot location on google maps>>>>>>\n")               #press ctrl+c to plot on map and exit 
            print("------------------------------------------------------------\n")

            
            data = f"PetId = {petID}, lat: {lat_in_degrees}, long: {long_in_degrees}"

            try:
                envelope = pubnub.publish().channel(channel).message({"data": data}).sync()
                print("Published:", data)
            except PubNubException as e:
                print("Publishing error:", e)

        time.sleep(0.1)
                        
except KeyboardInterrupt:
    print("Closing connection...")

    # Unsubscribe from the channel and stop PubNub instance
    pubnub.unsubscribe().channels(channel).execute()
    pubnub.stop()
    sys.exit(0)
