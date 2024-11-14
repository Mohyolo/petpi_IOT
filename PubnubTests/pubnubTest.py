#code references
#https://www.electronicwings.com/raspberry-pi/gps-module-interfacing-with-raspberry-pi
#https://www.pubnub.com/docs/sdks/python
#https://drive.google.com/drive/folders/1K0ZHI6oBDX4PYjixL9p1f6kPq-q0u7gS from https://www.youtube.com/watch?v=meT2WB369mc

###############################################################################
# Board: Raspberry Pi 3 (model B)
# Developed by: Akshay P Daga       Email: apdaga@gmail.com
# Programming Language: Python 
# This Program is just to demonstrate the Publish-Subscribe IoT Architecture
#
# Description:
# PUBNUB is the Broker/Server based on Public-Subscribe Architecture.
#
# STEPS:
# 1. Open a free account on https://www.pubnub.com/ 
#    a. Click on "Create New App" > Enter <Name for the App> > Click on "Create"
#    b. Click on the Newly created app
#    c. You can see that, Public Key and Subscribe Key
#    
# 2. Open Console for Debugging purpose
#    a. Go to  https://www.pubnub.com/docs/console
#    b. Copy and paste Public Key and Subscribe Key from step 1.c. to console window
#    c. Change the Name of the Channel to "Raspberry"
#    d. Click on the "SUBSCRIBE" > Conncection status will change to "CONNECTED" 
#    
#    e. Scroll down to (white) "message" window and write following in json format:
#    	  {"text":"Hi Guys"}
#    	  Click on "Send" button
# 	  
# 	  you will see the same message in black coloured message console.
# 	  
# 	  That means, It is working fine 
#    
# 3. Install punnub python library on your RPi3:
#    a. Open terminal on RPi3
#    b. type following command:
#       sudo pip install pubnub
# 	  
# 4. Place python script "ps_01.py" or "ps_02.py" on RPi3
#    Change Following 3 thing in these script:
#    a. pubnub publish_key  (from step 1.c)
#    b. pubnub subscibe_key (from step 1.c)
#    c. pubnub channel_name (from step 2.c)
#    
# 5. Run these Scripts on RPi3 using "Python2" IDE or in Terminal
#    
# 6. In this script, we are published and subcribed to the same borker.channel
#    Here, we are connecting/subscribing to the Borker.channel
#    then publishing the data once to the server/Broker.channel
#    and then reading the received msgs in infinite loop.
#    
# 7. We can Debug this program using pubnub console (https://www.pubnub.com/docs/console),
#    a. Run this script on RPi3 (as shown in step 5)
#    b. set publish_key, subscribe_key and channel_name in pubnub console same as the script,
#    c. and publish the data from pubnub console (as shown in step 2.e) 
#    
#    you can observer same msg received on RPi3 Terminal (where script is running)
#
######################################################################################    

# importing pubnub libraries
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub
import time


pnconf = PNConfiguration()                                              # create pubnub_configuration_object
 
pnconf.publish_key = 'pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76'       # set pubnub publish_key
pnconf.subscribe_key = 'sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64'     # set pubnub subscibe_key
pnconf.uuid = "Petpi2"                            

pubnub = PubNub(pnconf)                     # create pubnub_object using pubnub_configuration_object

channel='GPS-Petpi'                         # provide pubnub channel_name

data = {                                    # data to be published
    'username': 'Akshay: ps_01',
    'message' : 'This is my 1st msg... '
}

class MyListener(SubscribeCallback):        # Not need for working of this program
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            pubnub.publish().channel(channel).message({'fieldA': 'awesome', 'fieldB': 10}).sync()
 
    def message(self, pubnub, message):
        print(message)
 
    def presence(self, pubnub, presence):
        pass

my_listener = SubscribeListener()                   # create listner_object to read the msg from the Broker/Server
pubnub.add_listener(my_listener)                    # add listner_object to pubnub_object to subscribe it
pubnub.subscribe().channels(channel).execute()      # subscribe the channel (Runs in background)


my_listener.wait_for_connect()                      # wait for the listner_obj to connect to the Broker.Channel 
print('connected')                                  # print confirmation msg

pubnub.publish().channel(channel).message(data).sync()      # publish the data to the mentioned channel

try:
    while True:
        result = my_listener.wait_for_message_on(channel)  # Read the new msg on the channel
        print(result.message)                              # Print the new msg
        time.sleep(1)  # Just a delay to avoid spamming console
except KeyboardInterrupt:
    print("Closing connection...")

    # Unsubscribe from the channel and stop PubNub instance
    pubnub.unsubscribe().channels(channel).execute()
    pubnub.stop()
    print("Connection closed.")                                 # print the new msg