import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import cv2
import time

# Change session state based on page
st.session_state['current_page'] = 'student_perform'
FPS = 30

if 'received_movement' not in st.session_state:
    st.session_state['received_movement'] = False

def on_recv():
    '''
    convert incoming message to json msg
    if msg['command'] == 'mov':
        # get movement
    '''
    pass

def render_student_perform():
    st.title("Welcome to MirrorMe!")
    st.header("Waiting for teacher to send movement")
    frame_holder = st.empty()
    fps_counter = st.empty()
    exit_button = st.button("Exit")
    start_stop_button = st.empty()
    cap = cv2.VideoCapture(0)
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
        frame_holder.image(frame)
        # Spin loop to get 1/FPS FPS
        while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
            pass
        # Update FPS counter
        fps_counter.markdown(f"FPS: {str(1_000_000_000.0 / (time.monotonic_ns() - loop_start))}")
        # Handle Buttons
        if exit_button:
            cap.release()
            st.session_state['mqtt'].loop_stop()
            st.session_state['mqtt'].disconnect()
            switch_page("home")
    cap.release()

render_student_perform()