import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.runtime.scriptrunner import add_script_run_ctx
import json
import threading
import paho.mqtt.client as mqtt

# Change session state based on page
st.session_state['current_page'] = 'student_start'

if 'teacher_started' not in st.session_state:
    st.session_state['teacher_started'] = False

if 'pub' not in st.session_state:
    publisher = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    publisher.connect_async('test.mosquitto.org')
    publisher.loop_start()
    st.session_state['pub'] = publisher

def on_recv(client, userdata, message):
    print("Student Got Message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'start':
        st.session_state['teacher_started'] = True
        st.session_state['test'] = st.empty()

if 'sub' not in st.session_state:
    subscriber = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    subscriber.on_message = on_recv
    subscriber.connect_async('test.mosquitto.org')
    def thread_looper(client):
        client.loop_forever()
    sub_thread = threading.Thread(target=thread_looper, args=(subscriber,))
    add_script_run_ctx(sub_thread)
    st.session_state['sub'] = subscriber
    st.session_state['sub_thread'] = sub_thread

def render_student_start():
    st.title("Welcome to MirrorMe!")
    room_code = st.text_input(
        "Enter Room Code:",
        placeholder = "Room Code"
    )
    if room_code:
        st.session_state['room_code'] = room_code
        name = st.text_input(
            "Enter Name:",
            placeholder = "Name"
        )
        if name:
            if not st.session_state.get('joined_room', False):
                st.session_state['joined_room'] = True
                st.session_state['pub'].publish(f'mirrorme/student_{st.session_state["room_code"]}', json.dumps({"command": "join", "name": name}), qos=1)
                # TODO: For error reasons, assert that connection was actually made.
                #           Give a fault if it was not.
                st.session_state['sub'].on_connect = (lambda client, userdata, flags, rc: \
                                        client.subscribe(f'mirrorme/teacher_{st.session_state["room_code"]}', qos=1))
                st.session_state['sub_thread'].start()
                st.header(f"Joined Room: {st.session_state['room_code']}")
            exit_button = st.button("Exit", key="exit2")
            while True:
                if st.session_state.get('teacher_started', False):
                    switch_page("student_perform")
                if exit_button:
                    st.session_state['pub'].loop_stop()
                    st.session_state['pub'].disconnect()
                    st.session_state['sub'].loop_stop()
                    st.session_state['sub'].disconnect()
                    switch_page("home")
    if st.button("Exit", key="exit1"):
        st.session_state['pub'].loop_stop()
        st.session_state['pub'].disconnect()
        st.session_state['sub'].loop_stop()
        st.session_state['sub'].disconnect()
        switch_page("home")

render_student_start()