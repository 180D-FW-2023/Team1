from berryIMU import *
import time
import math
import bluetooth

def classify_jump(acc_arr):
    mag = math.sqrt(sum([x**2 for x in acc_arr]))
    if mag < 0.3:
        return True
    return False




def main():
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    print("Waiting for connection on RFCOMM channel", port)
    client_sock,address = server_sock.accept()
    print("Accepted connection from ",address)
    client_sock.settimeout(0)
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
                client_sock.send("jump")
                print("jump")
    imu.stop()
    sock.close()
        
if __name__ == "__main__":
    main()
