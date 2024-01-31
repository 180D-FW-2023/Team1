import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import cv2
import time
import movement
from model_utils import *

# Change session state based on page
st.session_state['current_page'] = 'teacher_record'

if 'recording' not in st.session_state:
    st.session_state['recording'] = False

if 'movement_recorded' not in st.session_state:
    st.session_state['movement_recorded'] = False

FPS = 30

def on_recv():
    '''
    convert incoming message to json msg
    if msg['command'] == 'exit':
        st.session_start['students'].remove(msg['name'])
    elif msg['command'] == 'score':
        st.session_start['students'].update({msg['name']: msg['score']})
    '''
    pass

def render_teacher_record():
    st.title("Record your Movement for your Students!")
    st.header(" ")
    cap = cv2.VideoCapture(0)
    frame_holder = st.empty()
    fps_counter = st.empty()
    exit_button = st.button("Exit")
    recording_button = st.empty()
    record = recording_button.button('Record', key='record')
    send_button = st.button("Send", disabled=True)
    while cap.isOpened():
        # Get loop start time
        loop_start = time.monotonic_ns()
        # Get frame
        ret, frame = cap.read()
        if not ret:
            break
        # Modify frame for viewing (flip, color, scaling)
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
        # If in idle mode
            # If have sent a recording before, play the recording, if not, then just display video
        # If in record mode
            # Record movement
        frame_holder.image(frame)
        # Spin loop to get 1/FPS FPS
        while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
            pass
        # Update FPS Counter
        fps_counter.markdown(f"FPS: {str(1_000_000_000.0 / (time.monotonic_ns() - loop_start))}")
        # Handle Buttons
        if exit_button:
            cap.release()
            st.session_state['mqtt'].loop_stop()
            st.session_state['mqtt'].disconnect()
            switch_page("home")
        if record:
            if st.session_state['recording'] == False:
                st.session_state['recording'] = True
                record = recording_button.button("Stop", key=f"stop{str(time.monotonic_ns())}")
            else:
                st.session_state['recording'] = False
                st.session_state['movement_recorded'] = True
                record = recording_button.button("Rerecord", key=f"rerecord{str(time.monotonic_ns())}")
            
        if send_button:
            st.session_state['mqtt'].publish('ece180d/test', "joe", qos=1)
            st.session_state['movement_recorded'] = True
    cap.release()

render_teacher_record()