import sys
from pubnub import Pubnub

pubnub = Pubnub(publish_key='pub-c-6478efda-63f9-4d8c-84ba-df3504a89d76', subscribe_key='sub-c-f8959022-48fd-4250-99bc-3a437eb6fd64')

channel = 'pi'

data = {
  'username': 'Petpi',
  'message': 'Hello World from Pi!'
}

def callback(m):
  print(m)

pubnub.publish(channel, data, callback=callback, error=callback)