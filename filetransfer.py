import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Client Connected to MQTT broker")
    else:
        print(f"Client failed to connect, return code: {rc}")




def publish_file(client, file_path, topic):
    with open(file_path, "rb") as file:
        chunk_size = 20000  # Set the size of each chunk
        chunk_number = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break  # End of file

            #topic_with_chunk = f"{topic}/{chunk_number}"
            
            result = client.publish(topic, chunk, qos=1)
            
            chunk_number += 1

            #time.sleep(0.1)  # Adjust as needed to avoid overwhelming the broker

def main():
    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("172.20.10.3")

    client.loop_start()
    time.sleep(2)

    file_path = "CAPTURE.mp4"
    topic = "video_transfer"

    publish_file(client, file_path, topic)

    client.disconnect()

if __name__ == "__main__":
    main()