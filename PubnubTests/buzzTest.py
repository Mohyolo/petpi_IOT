import RPi.GPIO as GPIO
import time
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException

class MyListener(SubscribeCallback):        # Not need for working of this program
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            pubnub.publish().channel(channel).message({'fieldA': 'awesome', 'fieldB': 10}).sync()
 
    def message(self, pubnub, message):
        print(message)
 
    def presence(self, pubnub, presence):
        pass


buz_pin = 23
GPIO.cleanup()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buz_pin,GPIO.OUT)

pnconf = PNConfiguration()                                              # create pubnub_configuration_object
 
pnconf.publish_key = 'pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76'       # set pubnub publish_key
pnconf.subscribe_key = 'sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64'     # set pubnub subscibe_key
pnconf.uuid = "Petpi"                            

pubnub = PubNub(pnconf)                     # create pubnub_object using pubnub_configuration_object

my_listener = SubscribeListener()                   # create listner_object to read the msg from the Broker/Server
pubnub.add_listener(my_listener)

channel='GPS-Petpi' 


try:
    while True:
        result = my_listener.wait_for_message_on(channel)  # Read the new msg on the channel
        print(result.message)                              # Print the new msg
        
        if result.message == "ON":
            GPIO.output(buz_pin,True)
        elif result.message == "OFF":
            GPIO.output(buz_pin,False)

        #time.sleep(1)  # Just a delay to avoid spamming console
except KeyboardInterrupt:
    print("Closing connection...")

    # Unsubscribe from the channel and stop PubNub instance
    pubnub.unsubscribe().channels(channel).execute()
    pubnub.stop()
    print("Connection closed.")
while True:
    GPIO.output(buz_pin,True)
    GPIO.output(buz_pin,False)