import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import cv2
import time
import movement
import json
from model_utils import *

# Change session state based on page
st.session_state['current_page'] = 'teacher_record'

if 'mode' not in st.session_state:
    st.session_state['mode'] = "idle"

if 'movement' not in st.session_state:
    st.session_state['movement'] = movement.Movement()

FPS = 30

def on_recv(client, userdata, message):
    print("Teacher got message")
    msg = json.loads(message.payload.decode("utf-8"))
    if 'command' not in msg or 'name' not in msg:
        return
    if msg['command'] == 'exit':
        del st.session_state['students'][msg['name']]
    elif msg['command'] == 'score':
        st.session_state['students'].update({msg['name']: msg['score']})

def record_on_click():
    if st.session_state['mode'] == "idle" or st.session_state['mode'] == "display":
        print("switching to record mode")
        st.session_state['mode'] = "record"
        st.session_state['movement'] = movement.Movement()
    elif st.session_state['mode'] == "record":
        print("switching to display mode")
        st.session_state['mode'] = "display"

def send_on_click():
    mov = st.session_state['movement'].get_movement_json()
    st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "movement", "mov" : mov}), qos=1)
    st.session_state['mode'] = "idle"

def exit_on_click():
    st.session_state['mqtt'].publish(f'mirrorme/teacher_{st.session_state["room_code"]}', json.dumps({"command": "exit"}), qos=1)
    st.session_state['mqtt'].disconnect()

def render_teacher_record():
    st.session_state['mqtt'].on_message = on_recv
    st.title("Record your Movement for your Students!")
    st.header(" ")
    st.markdown("Make sure your whole body is visible in the frame.")
    cap = cv2.VideoCapture(0)
    col1, col2 = st.columns([20,3])
    with col1:
        frame_holder = st.empty()
    with col2:
        st.subheader("Student Scores:" )
        student_scores = st.markdown("\n".join([f"{student}: {'N/A' if score is None else score}" for student, score in st.session_state['students'].items()]))
    fps_counter = st.empty()
    # st.header("Student Scores:" )
    # student_scores = st.markdown("\n".join([f"{student}: {'N/A' if score is None else score}" for student, score in st.session_state['students'].items()]))
    col1, col2, col3 = st.columns(3)
    with col1:
        exit_button = st.button("Exit", on_click=exit_on_click)
    with col2:
        recording_button = st.empty()
        record = recording_button.button(f'{"Record" if st.session_state["mode"] == "idle" else ("Rerecord" if st.session_state["mode"] == "display" else "Stop")}', on_click=record_on_click)
    with col3:
        send_button = st.empty()
        send = send_button.button("Send", disabled=(False if st.session_state['mode'] == "display" else True), on_click=send_on_click)
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
        new_points[POINT_JUMP] = False # TODO: get jump bool from IMU
        # Idle mode
        if st.session_state['mode'] == "idle":
            frame = movement.Movement.draw_stick_figure_simple(frame, new_points)
        elif st.session_state['mode'] == "record":
            frame = movement.Movement.draw_stick_figure_simple(frame, new_points)
            st.session_state['movement'].add_captured_points(new_points)
        elif st.session_state['mode'] == "display":
            if st.session_state['movement'].is_done():
                print("Restarting Movement")
                st.session_state['movement'].reset()
            frame = st.session_state['movement'].display_and_advance_frame(frame, new_points)
        frame_holder.image(frame)
        # Spin loop to get 1/FPS FPS
        while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
            pass
        # Update FPS Counter
        fps_counter.markdown(f"FPS: {str(int(100_000_000_000.0 / (time.monotonic_ns() - loop_start))/100.0)}")
        student_scores.markdown("\n".join([f"{student}: {'N/A' if score is None else score}" for student, score in st.session_state['students'].items()]))
        if exit_button:
            cap.release()
            switch_page("home")

    cap.release()

render_teacher_record()