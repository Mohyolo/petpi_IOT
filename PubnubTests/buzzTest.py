import RPi.GPIO as GPIO
import time

buz_pin = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buz_pin,GPIO.OUT)

for x in range(5):
    GPIO.output(buz_pin,True)
    time.sleep(0.3)
    GPIO.output(buz_pin,False)