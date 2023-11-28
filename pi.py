from berryIMU import *
import time
def main():
    imu = MirrorMeIMU()
    imu.start()
    for i in range(0, 1000):
        print(imu.get_values())
    imu.stop()

if __name__ == "__main__":
    main()
