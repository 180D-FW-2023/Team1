from berryIMU import *
import time
import math
def main():
    imu = MirrorMeIMU()
    imu.start()
    time.sleep(2)
    for i in range(0, 1_000_000):
        latest_data = imu.get_values()[-1]
        mag = math.sqrt(sum([x**2 for x in latest_data]))
        if mag < 0.3:
            print("jump")
            time.sleep(1)

        
if __name__ == "__main__":
    main()
