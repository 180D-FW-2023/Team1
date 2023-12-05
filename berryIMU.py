#!/usr/bin/python
#
#    This program  reads the angles from the acceleromteer, gyroscope
#    and mangnetometer on a BerryIMU connected to a Raspberry Pi.
#
#    This program includes two filters (low pass and median) to improve the
#    values returned from BerryIMU by reducing noise.
#
#    The BerryIMUv1, BerryIMUv2 and BerryIMUv3 are supported
#
#    This script is python 2.7 and 3 compatible
#
#    Feel free to do whatever you like with this code.
#    Distributed as-is; no warranty is given.
#
#    http://ozzmaker.com/
import sys
import time
import math
import IMU
import datetime
import os
import threading

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant

################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading values.


'''
Here is an example:
magXmin =  -1748
magYmin =  -1025
magZmin =  -1876
magXmax =  959
magYmax =  1651
magZmax =  708
Dont use the above values, these are just an example.
'''
############### END Calibration offsets #################

class MirrorMeIMU():

    BUF_LEN = 10

    def __init__(self):
        IMU.detectIMU()     #Detect if BerryIMU is connected.
        if(IMU.BerryIMUversion == 99):
            print(" No BerryIMU found... exiting ")
            sys.exit()
        IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass
        self.buffer = []
        self.thread = None
        self.event = threading.Event()
        self.event.clear()
        self.time = datetime.datetime.now()
    
    def start(self):
        self.event.set()
        self.thread = threading.Thread(target=self.__run)
        self.thread.start()

    def stop(self):
        self.event.clear()
        self.thread.join()
        self.buffer = []

    def get_values(self):
        return self.buffer

    def __run(self):
       while self.event.is_set():
            #Read the accelerometer values, convert to G
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            yG = (ACCx * 0.244)/1000
            xG = (ACCy * 0.244)/1000
            zG = (ACCz * 0.244)/1000


            ##################### END Tilt Compensation ########################

            values = [xG, yG, zG]
            self.buffer.append(values)
            if len(self.buffer) > MirrorMeIMU.BUF_LEN:
                self.buffer.pop(0)

