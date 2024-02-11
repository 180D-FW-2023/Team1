import RPi.GPIO as GPIO
import datetime
import os
import threading
import time

pin = 23
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.HIGH)
pin_frequency = 20
while True:
    if pin_frequency != 0:
        time.sleep(1/pin_frequency)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1/pin_frequency)
        GPIO.output(pin, GPIO.HIGH)