import streamlit as st
import random
from streamlit_extras.switch_page_button import switch_page
import paho.mqtt.client as mqtt
    
# Change session state based on page
st.session_state['current_page'] = 'teacher_start'
st.session_state['room_code'] = str(random.randint(0, 9999))
st.session_state['students'] = {'Aadhi': None, 'Esha': None}

# Create publisher object for teacher
publisher = mqtt.Client()
publisher.on_connect = (lambda client, userdata, flags, rc: print("Connection returned result: "+str(rc)) )
publisher.on_disconnect = (lambda client, userdata, rc: print(rc) )
publisher.on_message = (lambda client, userdata, message: print('got msg'))
publisher.connect_async('test.mosquitto.org')
publisher.loop_start()
st.session_state['pub'] = publisher

# TODO: create a student subscription

def on_recv():
    '''
    msg is json object
    msg received on student_room_code
    if msg['command'] == 'ping':
        # send ack message on teacher_room_code
    if msg['command'] == 'exit':
        st.session_start['students'].remove(msg['name'])
    elif msg['command'] == 'join':
        st.session_start['students'].update({msg['name']: None})
    '''
    pass

def render_teacher_start():
    st.title("Welcome to MirrorMe!")
    st.header(f"Room Code: {st.session_state['room_code']}")
    st.header(" ")
    st.header("Students Joined:" )
    st.write(st.session_state.students)
    if st.button("Exit"):
        st.session_state['pub'].loop_stop()
        st.session_state['pub'].disconnect()
        switch_page("home")
    if st.button("Start"):
        st.session_state['pub'].publish(f'mirrome/teacher_{st.session_state["room_code"]}', "joe", qos=1)
        switch_page("teacher_record")

render_teacher_start()