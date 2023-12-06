from berryIMU import *
import time
import math
import bluetooth

def classify_jump(acc_arr):
    mag = math.sqrt(sum([x**2 for x in acc_arr]))
    if mag < 0.3:
        return True
    return False

bd_addr = "F0:9E:4A:69:A9:41"
port = 4



def main():
    sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((bd_addr, port))
    imu = MirrorMeIMU()
    time.sleep(2)
    imu.start()
    while True:
        # command = "" #TODO: get command
        # if command == "start":
        #     imu.start()
        # elif command == "stop":
        #     imu.stop()
        # elif command == "exit":
        #     break
        buf = imu.get_values()
        if len(buf) > 0:
            if classify_jump(buf[-1]) is True:
                sock.send("jump")
                print("jump")
    imu.stop()
    sock.close()
        
if __name__ == "__main__":
    main()
