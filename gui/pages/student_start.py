import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.runtime.scriptrunner import add_script_run_ctx
import json
import threading
import paho.mqtt.client as mqtt
import time

# Change session state based on page
st.session_state['current_page'] = 'student_start'

if 'teacher_started' not in st.session_state:
    st.session_state['teacher_started'] = False

if 'valid_room' not in st.session_state:
    st.session_state['valid_room'] = False

if 'tried_joining_invalid_room' not in st.session_state:
    st.session_state['tried_joining_invalid_room'] = False

def on_recv(client, userdata, message):
    print("Student Got Message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'ack':
        st.session_state['valid_room'] = True
    if msg['command'] == 'start':
        st.session_state['teacher_started'] = True

if 'mqtt' not in st.session_state:
    mqtt_client = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    mqtt_client.on_message = on_recv
    mqtt_client.connect_async('test.mosquitto.org')
    def thread_looper(client):
        client.loop_forever()
    mqtt_thread = threading.Thread(target=thread_looper, args=(mqtt_client,))
    add_script_run_ctx(mqtt_thread)
    st.session_state['mqtt'] = mqtt_client
    st.session_state['mqtt_thread'] = mqtt_thread

def render_student_start():
    st.title("Welcome to MirrorMe!")
    if st.session_state.get('tried_joining_invalid_room', False):
        st.title("Invalid Room Code. Try again.")
    room_code = st.text_input(
        "Enter Room Code:",
        placeholder = "Room Code",
        key = "2"
        # TODO: disable text box once filled in
    )
    if room_code:
        st.session_state['room_code'] = room_code
        name = st.text_input(
            "Enter Name:",
            placeholder = "Name",
            key = "1"
            # TODO: disable text box once filled in
        )
        if name:
            if not st.session_state.get('joined_room', False):
                st.session_state['name'] = name
                st.session_state['mqtt'].publish(f'mirrorme/student_{st.session_state["room_code"]}', json.dumps({"command": "join", "name": name}), qos=1)
                # TODO: For error reasons, assert that connection was actually made.
                #           Give a fault if it was not.
                st.session_state['mqtt'].on_connect = (lambda client, userdata, flags, rc: \
                                        client.subscribe(f'mirrorme/teacher_{st.session_state["room_code"]}', qos=1))
                # TODO: check if room already exists, if it doesn't, refresh the page
                st.session_state['mqtt_thread'].start()
                loop_start = time.monotonic_ns()
                while time.monotonic_ns() < loop_start + (1_000_000_000):
                    pass
                if not st.session_state.get('valid_room', False):
                    st.session_state['tried_joining_invalid_room'] = True
                    switch_page("home")
                st.header(f"Joined Room: {st.session_state['room_code']}")
                st.session_state['joined_room'] = True
            exit_button = st.button("Exit", key="exit2")
            while True:
                if st.session_state.get('teacher_started', False):
                    switch_page("student_perform")
                if exit_button:
                    st.session_state['mqtt'].disconnect()
                    switch_page("home")
    if st.button("Exit", key="exit1"):
        if st.session_state.get('joined_room', False):
            st.session_state['mqtt'].publish(f'mirrorme/student_{st.session_state["room_code"]}', json.dumps({"command": "exit", "name": st.session_state['name']}), qos=1)
        st.session_state['mqtt'].disconnect()
        switch_page("home")

render_student_start()