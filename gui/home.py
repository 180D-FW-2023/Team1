import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_lottie import st_lottie
import paho.mqtt.client as mqtt
import threading
import time
import json

# Change session state based on page
top_header = st.markdown("‎ ‎")
if st.session_state.get('message', False):
    top_header.markdown(st.session_state['message'])
# If not redirected from home page, clear session state
if st.session_state.get('current_page', None) != 'home':
    st.session_state.clear()
st.session_state['current_page'] = 'home'

if 'mirrormodule_name' not in st.session_state:
    st.session_state['mirrormodule_name'] = None

if 'mirrormodule_mqtt' not in st.session_state:
    mqtt_client = mqtt.Client()
    # TODO: For error reasons, assert that connection was actually made.
    #           Give a fault if it was not.
    mqtt_client.connect_async('test.mosquitto.org')
    def thread_looper(client):
        client.loop_forever()
    mqtt_thread = threading.Thread(target=thread_looper, args=(mqtt_client,))
    add_script_run_ctx(mqtt_thread)
    st.session_state['mirrormodule_mqtt'] = mqtt_client
    st.session_state['mirrormodule_mqtt_thread'] = mqtt_thread
    st.session_state['mirrormodule_mqtt_thread'].start()

if 'valid_mirrormodule' not in st.session_state:
    st.session_state['valid_mirrormodule'] = False

def mirrormodule_on_recv(client, userdata, message):
    print("Got message from MirrorModule")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'valid':
        st.session_state['valid_mirrormodule'] = True


with open('gui/style.css') as f:    
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_home_page():
    col1, col2 = st.columns([2, 10])
    with col1:
        st_lottie('https://lottie.host/edb12174-1102-4fc5-a7b7-e695bf7b52c2/ui94YFdvMi.json', key="user")
    with col2:
        st.title("Welcome to MirrorMe!")
    mirrormodule_input = st.empty()
    mirrormodule_name = mirrormodule_input.text_input(
            "Enter Your MirrorModule ID. Leave blank if you not using a MirrorModule.",
            placeholder="MirrorModule ID",
            disabled=False
    )
    print(mirrormodule_name)
    if mirrormodule_name:
        st.session_state['mirrormodule_name'] = mirrormodule_name
        st.session_state['mirrormodule_mqtt'].on_connect = (lambda client, userdata, flags, rc: \
                                        client.subscribe(f'mirrorme/mirrormodule_{st.session_state["mirrormodule_name"]}', qos=1))
        st.session_state['mirrormodule_mqtt'].on_message = mirrormodule_on_recv
        st.session_state['mirrormodule_mqtt'].subscribe(f'mirrorme/mirrormodule_{st.session_state["mirrormodule_name"]}', qos=1)
        st.session_state['mirrormodule_mqtt'].publish(f'mirrorme/mirrormodule_{st.session_state["mirrormodule_name"]}', json.dumps({"command": "ping"}), qos=1)
        loop_start = time.monotonic_ns()
        while (time.monotonic_ns() < loop_start + (2_000_000_000)) and not st.session_state.get('valid_mirrormodule', False):
            # Timeout for validating MirrorModule name
            pass
        if not st.session_state.get('valid_mirrormodule', False):
            top_header.markdown("Invalid MirrorModule ID. Please Try Again.")
        else:
            mirrormodule_input.text_input(
                    "Enter Your MirrorModule ID. Leave blank if you not using a MirrorModule.",
                    placeholder=st.session_state["mirrormodule_name"],
                    disabled=True
            )
            top_header.markdown("Connected to MirrorModule. Please Continue.")
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([5.2, 5, 5])
        with col2:
            st.header("Join As:")
        col1, col2, col3, col4 = st.columns([1.7,2.5,2.5,2])
        with col2:
            if st.button("Teacher", use_container_width=True):
                switch_page("teacher_start")
        with col3:
            if st.button("Student", use_container_width=True):
                switch_page("student_start")

render_home_page()
