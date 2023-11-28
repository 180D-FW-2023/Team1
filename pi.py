from BerryIMU.python_BerryIMU_gyro_accel_compass_filters.berryIMU import *
import time
def main():
    imu = MirrorMeIMU()
    imu.start()
    time.sleep(2)
    imu.get_values()
    time.sleep(2)
    imu.get_values()
    imu.stop()
    time.sleep(3)
    imu.get_values()
    time.sleep(1)
    imu.get_values()

if __name__ == "__main__":
    main()