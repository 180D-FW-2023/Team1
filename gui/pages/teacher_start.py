import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.runtime.scriptrunner import add_script_run_ctx
import paho.mqtt.client as mqtt
import random
import string
import json
import threading
    
# Change session state based on page
st.session_state['current_page'] = 'teacher_start'

# Generate random room code
if 'room_code' not in st.session_state:
    st.session_state['room_code'] = "".join(random.choices(string.ascii_uppercase, k=4))

# Initialize list of students
if 'students' not in st.session_state:
    st.session_state['students'] = {'Aadhi': None, 'Esha': None}

# Create publisher object for teacher
if 'pub' not in st.session_state:
    publisher = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    publisher.connect_async('test.mosquitto.org')
    publisher.loop_start()
    st.session_state['pub'] = publisher

# On receive callback for student channel
def on_recv(client, userdata, message):
    print("Teacher got message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg or 'name' not in msg:
        return
    if msg['command'] == 'ping':
       pass
    elif msg['command'] == 'exit':
        st.session_state['students'].remove(msg['name'])
    elif msg['command'] == 'join':
        st.session_state['students'].update({msg['name'] : None})

if 'sub' not in st.session_state:
    subscriber = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    subscriber.on_connect = (lambda client, userdata, flags, rc: \
                            client.subscribe(f'mirrorme/student_{st.session_state["room_code"]}', qos=1))
    subscriber.on_message = on_recv
    subscriber.connect_async('test.mosquitto.org')
    def thread_looper(client):
        client.loop_forever()
    sub_thread = threading.Thread(target=thread_looper, args=(subscriber,))
    add_script_run_ctx(sub_thread)
    sub_thread.start()
    st.session_state['sub'] = subscriber
    st.session_state['sub_thread'] = sub_thread

def render_teacher_start():
    st.title("Welcome to MirrorMe!")
    st.header(f"Room Code: {st.session_state['room_code']}")
    st.header(" ")
    st.header("Students Joined:" )
    st.write(st.session_state.students)
    if st.button("Exit"):
        st.session_state['pub'].loop_stop()
        st.session_state['pub'].disconnect()
        st.session_state['sub'].loop_stop()
        st.session_state['sub'].disconnect()
        switch_page("home")
    if st.button("Start"):
        st.session_state['pub'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "start"}), qos=1)
        switch_page("teacher_record")

render_teacher_start()