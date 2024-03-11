from pi_files.berryIMU import *
from pi_files.LSM6DSL import *
import time
import math
import bluetooth
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import socket
import json
import smbus

pin = 16
is_mqtt = False
is_bluetooth = False
mqtt_client = mqtt.Client()
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)


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


def on_connect(client, userdata, flags, rc):
    print(client,rc,userdata,flags)
    client.subscribe(f'mirrorme/mirrormodule_{socket.gethostname()}', qos=1)
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

def double_tap_callback(channel):
    global mqtt_client
    mqtt_client.publish(f'mirrorme/mirrormodule_{socket.gethostname()}', json.dumps({"command": "record"}), qos=1)
    print("double tap detected")


GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(INTERRUPT_PIN, GPIO.RISING, callback=double_tap_callback, bouncetime=300)
pin_frequency = 0


def set_pin_frequency(freq):
    pin_frequency = freq

def classify_jump(acc_arr):
    mag = math.sqrt(sum([x**2 for x in acc_arr]))
    if mag < 0.3:
        return True
    return False

def mirrormodule_on_recv(client, userdata, message):
    print("Got message from Laptop")
    global is_mqtt
    global pin_frequency
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'ping':
        is_mqtt = True
        client.publish(f'mirrorme/mirrormodule_{socket.gethostname()}', json.dumps({"command": "valid"}), qos=1)
    elif msg['command'] == 'score':
        pin_frequency = msg['score']
        print(pin_frequency)

def main(mqtt_client):
    global is_bluetooth
    global is_mqtt
    global pin_frequency

    print(socket.gethostname())
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.settimeout(0)
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = mirrormodule_on_recv
    mqtt_client.connect_async('test.mosquitto.org')
    mqtt_client.on_message = mirrormodule_on_recv
    mqtt_client.loop_start()
    print(f'mirrorme/mirrormodule_{socket.gethostname()}')
    mqtt_client.subscribe(f'mirrorme/mirrormodule_{socket.gethostname()}', qos=1)
    mqtt_client.on_message = mirrormodule_on_recv
    print("Waiting for connection on RFCOMM channel", port)
    while(is_mqtt == False and is_bluetooth == False):
        try:
            client_sock,address = server_sock.accept()
            if client_sock:
                is_bluetooth = True
                print("Accepted connection from ",address)
                client_sock.settimeout(0)
        except:
            pass
    imu = MirrorMeIMU()
    time.sleep(2)
    imu.start()
    while True:
        if pin_frequency != 0:
            time.sleep(1/pin_frequency)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(1/pin_frequency)
            GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.LOW)
        buf = imu.get_values()
        if(is_bluetooth):
            try:
                data = client_sock.recv(1024)
                if data != "":
                    data = 100 - int(float(data.decode('utf-8')))
                    print(data)
                    if data >= 0 and data <= 100:
                        pin_frequency = data
            except:
                pin_frequency = 0
        if len(buf) > 0:
            if classify_jump(buf[-1]) is True:
                if(is_bluetooth):
                    client_sock.send("jump")
                else:
                    mqtt_client.publish(f'mirrorme/mirrormodule_{socket.gethostname()}', json.dumps({"command": "jump"}), qos=1)
                print("jump")
    imu.stop()
    sock.close()
        
if __name__ == "__main__":
    main(mqtt_client)
