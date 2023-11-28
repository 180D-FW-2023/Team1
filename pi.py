from BerryIMU.python_BerryIMU_gyro_accel_compass_filters.berryIMU import *
from BerryIMU.python_BerryIMU_gyro_accel_compass_filters.IMU import *
import time
def main():
    imu = MirrorMeIMU()
    imu.start()
    time.sleep(2)
    print(imu.get_values())
    time.sleep(2)
    print(imu.get_values())
    imu.stop()
    time.sleep(3)
    print(imu.get_values())
    time.sleep(1)
    print(imu.get_values())

if __name__ == "__main__":
    main()