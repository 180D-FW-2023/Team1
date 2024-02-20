from pi_files.berryIMU import *
import time
import math
import bluetooth
import RPi.GPIO as GPIO

pin = 23
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.HIGH)
pin_frequency = 20

def set_pin_frequency(freq):
    pin_frequency = freq

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
        if pin_frequency != 0:
            time.sleep(1/pin_frequency)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(1/pin_frequency)
            GPIO.output(pin, GPIO.HIGH)
        buf = imu.get_values()
        if len(buf) > 0:
            if classify_jump(buf[-1]) is True:
                client_sock.send("jump")
                print("jump")
    imu.stop()
    sock.close()
        
if __name__ == "__main__":
    main()
