import signal
from LSM6DSL import *
import sys
import RPi.GPIO as GPIO
import smbus
bus = smbus.SMBus(1)
INTERRUPT_PIN = 12
#Used to write to the IMU
def writeByte(device_address,register,value):
    bus.write_byte_data(device_address, register, value)

writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01100000)                 #ODR_XL = 416 Hz, FS_XL = +/- 2 g
writeByte(LSM6DSL_ADDRESS,LSM6DSL_TAP_CFG,0b10001110)                  #Enable interrupts and tap detection on X, Y, Z-axis
writeByte(LSM6DSL_ADDRESS,LSM6DSL_TAP_THS_6D,0b10001100)               #Set tap threshold
writeByte(LSM6DSL_ADDRESS,LSM6DSL_INT_DUR2,0b01111111)                 #Set Duration, Quiet and Shock time windows
writeByte(LSM6DSL_ADDRESS,LSM6DSL_WAKE_UP_THS,0b10000000)              #Double-tap enabled 
writeByte(LSM6DSL_ADDRESS,LSM6DSL_MD1_CFG,0b00001000)                  #Double-tap interrupt driven to INT1 pin

def double_tap_callback(channel):
    print("double tap detected")

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=double_tap_callback, bouncetime=300)

while True:
    pass