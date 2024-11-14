#code is from the below tutorial
#https://www.youtube.com/watch?v=QH1umP-duik

import time
import board
import busio
import adafruit_adxl34x
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub


i2c = busio.I2C(board.SCL,board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)
pnconf = PNConfiguration()                                              # create pubnub_configuration_object
 
pnconf.publish_key = 'pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76'       # set pubnub publish_key
pnconf.subscribe_key = 'sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64'     # set pubnub subscibe_key
pnconf.uuid = "Petpi"                            

pubnub = PubNub(pnconf)                     # create pubnub_object using pubnub_configuration_object

channel='GPS-Petpi' 

message = {                                    # data to be published
    'username': 'Akshay: ps_01',
    'message' : 'This is my 1st msg... '
}

data = "%f %f %f" % accelerometer.acceleration

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
print('connected')

pubnub.publish().channel(channel).message(message).sync()


try:
    while True:
        data = "%f %f %f" % accelerometer.acceleration         # Format data

        # Publish the data
        try:
            envelope = pubnub.publish().channel(channel).message({"data": data}).sync()
            print("Published:", data)
        except PubNubException as e:
            print("Publishing error:", e)

        time.sleep(1)  # Wait for 1 second before the next publish
except KeyboardInterrupt:
    print("Closing connection...")

    # Unsubscribe from the channel and stop PubNub instance
    pubnub.unsubscribe().channels(channel).execute()
    pubnub.stop()
    print("Connection closed.")