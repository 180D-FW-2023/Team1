import Rpi.GPIO as GPIO
import datetime
import os
import threading
import time

class HapticBuzzer():
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.thread = None
        self.event = threading.Event()
        self.event.clear()
        self.pin_frequency = 0

    def start(self):
        self.event.set()
        self.thread = threading.Thread(target=self.__run)
        self.thread.start()

    def stop(self):
        self.event.clear()
        self.thread.join()

    def set_pin_frequency(self, freq):
        self.pin_frequency = freq

    def __run(self):
        while self.pin_frequency != 0:
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(1/self.pin_frequency)
            GPIO.output(self.pin, GPIO.HIGH)