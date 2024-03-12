import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import cv2
import time
import json
import movement
import threading
from model_utils import *

st.set_page_config(layout="wide")
# Change session state based on page
st.session_state['current_page'] = 'student_perform'
FPS = 30

if 'mode' not in st.session_state:
    st.session_state['mode'] = "waiting"

if 'score' not in st.session_state:
    st.session_state['score'] = None

if 'jump_buffer' not in st.session_state:
    st.session_state['jump_buffer'] = False
    st.session_state['jump_mutex'] = threading.Lock()

if 'last_mode_change' not in st.session_state:
    st.session_state['last_mode_change'] = time.monotonic_ns()

def mirrorme_on_recv(client, userdata, message):
    print("Student got message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'exit':
       st.session_state['valid_room'] = False
    elif msg['command'] == 'movement':
        st.session_state['mode'] = "idle"
        st.session_state['score'] = None
        mov = msg['mov']
        st.session_state['movement'] = movement.Movement(mov)

def mirrormodule_on_recv(client, userdata, message):
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg:
        return
    if msg['command'] == 'record':
        if st.session_state['mode'] == "idle":
            st.session_state['mode'] = "performing"
        elif st.session_state['mode'] == "performing":
            pass
    elif msg['command'] == 'jump':
        print("Got jump")
        if st.session_state['mode'] == "performing":
            with st.session_state['jump_mutex']:
                st.session_state['jump_buffer'] = True

def start_stop_on_click():
    if st.session_state['mode'] == "idle":
        st.session_state['mode'] = "performing"
    elif st.session_state['mode'] == "performing":
        st.session_state['mode'] = "idle"

def render_student_perform():
    st.session_state['mqtt'].on_message = mirrorme_on_recv
    if st.session_state.get("mirrormodule_name", None) is not None:
        st.session_state['mirrormodule_mqtt'].on_message = mirrormodule_on_recv
    col1, col2, col3 = st.columns([5, 20,3])
    message = st.empty()
    with col2:
        st.markdown("Make sure your whole body is visible in the frame.")
        frame_holder = st.empty()
        fps_counter = st.empty()
        exit_button = st.button("Exit")
        start_stop_button = st.empty()
        start_stop_button.button("Start/Stop", key=str(time.monotonic_ns()), on_click=start_stop_on_click)
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
            new_points = StickFigureEstimator.generate_points(frame)
            new_points[POINT_JUMP] = False 
            with st.session_state['jump_mutex']:
                if st.session_state['jump_buffer']:
                    new_points[POINT_JUMP] = True
                    st.session_state['jump_buffer'] = False
            
            # Waiting for a movement mode
            if st.session_state['mode'] == "waiting":
                message.header("Waiting for Teacher to Send Movement.")
                frame = movement.Movement.draw_stick_figure_simple(frame, new_points)
            
            # Waiting to start performing mode
            elif st.session_state['mode'] == "idle":
                st.session_state['movement'].reset()
                if st.session_state['score'] is None:
                    message.header("Got a new movement from Teacher. Press Start to perform.")
                else:
                    message.header(f"You got a score of {st.session_state['score']}!. Press Start to try again!")
                frame = movement.Movement.draw_stick_figure_simple(frame, new_points)
        
            # Performing movement mode
            elif st.session_state['mode'] == "performing":
                message.header("Performing movement. Press Stop to Cancel.")
                if not st.session_state['movement'].is_done():
                    frame = st.session_state['movement'].display_and_advance_frame(frame, new_points)
                    score = st.session_state['movement'].get_score()
                    curr_score = st.session_state['movement'].get_current_score()
                    if st.session_state.get("mirrormodule_name", None) is not None:
                        st.session_state['mirrormodule_mqtt'].publish(f'mirrorme/mirrormodule_{st.session_state["mirrormodule_name"]}', \
                                        json.dumps({"command": "score", "score": curr_score}), qos=1)
                    st.session_state['score'] = score
                else:
                    score = st.session_state['movement'].get_score()
                    st.session_state['mqtt'].publish(f'mirrorme/student_{st.session_state["room_code"]}', json.dumps({"command": "score", "name": st.session_state['name'], "score": score}), qos=1)
                    st.session_state['mode'] = "idle"
            
            frame_holder.image(frame, use_column_width=True)

            # Spin loop to get 1/FPS FPS
            while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
                pass
                        
            # Handle Buttons
            if exit_button or not st.session_state.get('valid_room', False):
                cap.release()
                # If room was closed
                if not st.session_state.get('valid_room', False):
                    st.session_state['message'] = 'Teacher Closed Room.'
                # If exit button was pressed
                else:
                    st.session_state['mqtt'].publish(f'mirrorme/student_{st.session_state["room_code"]}', json.dumps({"command": "exit", "name": st.session_state['name']}), qos=1)
                st.session_state['mqtt'].disconnect()
                switch_page("home")
        cap.release()

render_student_perform()