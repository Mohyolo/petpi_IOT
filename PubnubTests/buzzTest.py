import RPi.GPIO as GPIO
import time

buz_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buz_pin,GPIO.OUT)

while True:
    GPIO.output(buz_pin,True)
    GPIO.output(buz_pin,False)

GPIO.cleanup()

