from berryIMU import *
import time
import math

def classify_jump(acc_arr):
    mag = math.sqrt(sum([x**2 for x in acc_arr]))
    if mag < 0.3:
        return True
    return False

def main():
    imu = MirrorMeIMU()
    time.sleep(2)
    while True:
        command = "" #TODO: get command
        if command == "start":
            imu.start()
        elif command == "stop":
            imu.stop()
        elif command == "exit":
            break
        buf = imu.get_values()
        if len(buf) > 0:
            if classify_jump(buf[-1]) is True:
                pass # SEND JUMP COMMAND
        
if __name__ == "__main__":
    main()
