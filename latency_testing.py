import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc):
    print(client,rc,userdata,flags)
    client.subscribe(f'mirrorme/mirrormodule_raspberrypi', qos=1)
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

def mirrormodule_on_recv(client, userdata, message):
    global time_start
    global csv
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'valid':
        time_end = time.time()
        csv.write(str(time_end - time_start) + ",\n")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = mirrormodule_on_recv
#mqtt_client.connect_async('test.mosquitto.org')
mqtt_client.connect("172.20.10.3")

mqtt_client.loop_start()
print(f'mirrorme/mirrormodule_raspberrypi')
mqtt_client.subscribe(f'mirrorme/mirrormodule_raspberrypi', qos=1)



csv = open("brokerlatptop.csv", "a")  # append mode
time.sleep(2)
for i in range(100):
    time_start = time.time()
    mqtt_client.publish(f'mirrorme/mirrormodule_raspberrypi', json.dumps({"command": "ping"}), qos=1)
    time.sleep(0.2)
    
csv.close()
