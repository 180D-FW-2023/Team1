import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.runtime.scriptrunner import add_script_run_ctx
import paho.mqtt.client as mqtt
import random
from streamlit_lottie import st_lottie
import string
import json
import threading
import time
    
# Change session state based on page
st.session_state['current_page'] = 'teacher_start'

# Generate random room code
if 'room_code' not in st.session_state:
    st.session_state['room_code'] = "".join(random.choices(string.ascii_uppercase, k=4))

# Initialize list of students
if 'students' not in st.session_state:
    st.session_state['students'] = {}


# On receive callback for student channel
def on_recv(client, userdata, message):
    print("Teacher got message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg or 'name' not in msg:
        return
    if msg['command'] == 'exit':
        del st.session_state['students'][msg['name']]
    elif msg['command'] == 'join':
        st.session_state['students'].update({msg['name'] : None})
        st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "ack", "name" : st.session_state['teacher_name']}), qos=1)

# Create MQTT object
if 'mqtt' not in st.session_state:
    mqtt_client = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    mqtt_client.on_connect = (lambda client, userdata, flags, rc: \
                            client.subscribe(f'mirrorme/student_{st.session_state["room_code"]}', qos=1))
    mqtt_client.on_message = on_recv
    mqtt_client.connect_async('test.mosquitto.org')
    def thread_looper(client):
        client.loop_forever()
    mqtt_thread = threading.Thread(target=thread_looper, args=(mqtt_client,))
    add_script_run_ctx(mqtt_thread)
    mqtt_thread.start()
    st.session_state['mqtt'] = mqtt_client


def render_teacher_start():
    col1, col2 = st.columns([2, 10])
    with col1:
        st_lottie('https://lottie.host/edb12174-1102-4fc5-a7b7-e695bf7b52c2/ui94YFdvMi.json', key="user")
    with col2:
        st.title("Welcome to MirrorMe!")
    container = st.empty()
    container.header("Create a Room For Your Students!")
    name = container.text_input(
            "Enter Your Name: ",
            placeholder = "Name",
            # TODO: disable text box once filled in
        )
    if name:
        st.session_state['teacher_name'] = name
        container.empty()
        st.header(f"Room Code: {st.session_state['room_code']}")
        st.header("Students Joined:" )
        students = st.empty()
        #TODO: Style a container with the student's names in it once mqtt stuff fixed
        with open('gui/style.css') as f:    
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2.5,1,1,2])
        with col2:
            exit_button2 = st.button("Exit", key="exit2")
        with col3:
            start_button = st.button("Start")
        while True:
            students.markdown(", ".join(st.session_state['students'].keys()))
            time.sleep(0.1)
            if exit_button2:
                st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "exit"}), qos=1)
                st.session_state['mqtt'].disconnect()
                switch_page("home")
            if start_button:
                st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "start"}), qos=1)
                switch_page("teacher_record")
    exit_button = st.button("Exit", use_container_width=True)
    if exit_button:
        st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "exit"}), qos=1)
        st.session_state['mqtt'].disconnect()
        switch_page("home")

render_teacher_start()
