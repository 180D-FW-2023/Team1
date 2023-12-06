import streamlit as st
import cv2
import os
import tempfile
import numpy as np
#import speech_recognition as sr
import threading
import movement 
from model_utils import StickFigureEstimator
import time
#import pyttsx3


FPS = 24

# Function to convert OpenCV image format to Streamlit format
def opencv_to_streamlit(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)\


operating_system = os.environ.get('OS', '')

# Initialize webcam
# cap = cv2.VideoCapture(0)
# codec = cv2.VideoWriter_fourcc(*'XVID')

# Hide the sidebar
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def student_page():
    st.title("Follow the actions on the screen!")
    st.header("Score:")
    # video_file = open('CAPTURE.mp4','rb')
    # video_bytes = video_file.read()
    # st.video(video_bytes)

# def callback(recognizer, audio):                          # this is called from the background thread
#     try:
#         ans = recognizer.recognize_google(audio)
#         print("You said " + ans)  # received audio data, now need to recognize it
#         if ans == 'start':
#             st.session_state['start'] = 1
#         else:
#             st.session_state['start'] = 0
#         if ans == 'stop':
#             st.session_state['stop'] = 1
#         else:
#             st.session_state['stop'] = 0
#     except sr.RequestError:
#         print("Google not available") 
#     except sr.UnknownValueError:
#         print("Can't understand")



def teacher_page():
    st.title("Show your students what to do!")
    st.header("Webcam Live Feed")
    recording = False
    # r = sr.Recognizer()
    # r.listen_in_background(sr.Microphone(), callback)
    
    # Session state for recording flag and path of the recorded video
    # if 'recording' not in st.session_state:
    #     st.session_state['recording'] = False
    # if 'recorded_video' not in st.session_state:
    #     st.session_state['recorded_video'] = None
    # Button to start/stop recording
    if 'first' not in st.session_state:
        st.session_state['first'] = True
    if 'second' not in st.session_state:
        st.session_state['second'] = False
    if 'third' not in st.session_state:
        st.session_state['third'] = False
    container_2 =  st.empty()
    container_3 = st.empty()
    recording = 0
    if os.path.isfile("CAPTURE.mp4"):
            video_file = open('CAPTURE.mp4','rb')
            video_bytes = video_file.read()
            frame_holder = container_3.video(video_bytes)
    
    if st.session_state['first']:
        print("first state")
        start_btN = container_2.button("Record")
        frame_holder = container_3.empty()
        recording = 1
        if start_btN:
            print("clicked start button")
            st.session_state['second'] = True
            st.session_state['first'] = False
            st.rerun()

    elif st.session_state['second']:
        print("second state")
        end_bTN = container_2.button("Stop Recording")
        frame_holder = container_3.empty()
        recording = 1
        if end_bTN:
            print("clicked stop recording button")
            st.session_state['third'] = True
            st.session_state['second'] = False
            st.rerun()

    elif st.session_state['third']:
        print("third state")
        with container_2:
            col1, col2 = st.columns(2)
            with col1:
                restart_btN = st.button("Re-Record")
            with col2:
                send_btN = st.button("Send")
        frame_holder = container_3.empty()
        recording = 0
        if restart_btN:
            print("clicked restart button")
            st.session_state['second'] = True
            st.session_state['third'] = False
            st.session_state.mov = movement.Movement()
            st.rerun()
        elif send_btN:
            print("clicked send button")
            st.session_state['first'] = True
            st.session_state['third'] = False
            st.rerun()



    # Initialize webcam
    
    cap = cv2.VideoCapture(0)
    if 'Windows' in operating_system:
        codec = cv2.VideoWriter_fourcc(*'H264')
    else:
        codec = cv2.VideoWriter_fourcc(*'MJPG')
    output = None

        

    if 'mov' not in st.session_state:
        st.session_state.mov = movement.Movement()
    # Continuous loop to update the live feed and handle recording
    while cap.isOpened():
        # Get loop start time
        loop_start = time.monotonic_ns()

        # Get frame
        ret, frame = cap.read()
        if not ret:
            break

        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)

        # If in recording mode, add points to movement object
        if st.session_state['second']:
            new_points = StickFigureEstimator.generate_points(frame)
            frame = StickFigureEstimator.overlay_points(frame, new_points)
            new_points[movement.Movement.POINT_JUMP] = False # TODO: get jump bool from IMU
            st.session_state.mov.add_captured_points(new_points)
        elif st.session_state['third']:
            if st.session_state.mov.is_done():
                st.session_state.mov.reset()
            frame = st.session_state.mov.display_and_advance_frame(frame)

        # Convert the color format for Streamlit
        frame = opencv_to_streamlit(frame)
        frame_holder.image(frame)

        # Spin loop to get 1/FPS FPS
        while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
            pass

    cap.release()
    


# Initialize session state for page tracking
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'
# if 'first' not in st.session_state:
#     st.session_state['first'] = True
# if 'second' not in st.session_state:
#     st.session_state['second'] = False
# if 'third' not in st.session_state:
#     st.session_state['third'] = False


# if 'start' not in st.session_state:
#     st.session_state['start'] = 0
# if 'stop' not in st.session_state:
#     st.session_state['stop'] = 0

# Define a function to change the page
def change_page(page_name):
    st.session_state['current_page'] = page_name

# Display the home page with buttons
def home_page():
    st.title("Welcome to MirrorMe!")
    st.header("Join As:")
    col1, col2 = st.columns(2)
    with col1:
        # Pass a function reference and arguments
        st.button("Teacher", on_click=change_page, args=('teacher',))
    with col2:
        # Pass a function reference and arguments
        st.button("Student", on_click=change_page, args=('student',))

# Page rendering based on session state
if st.session_state['current_page'] == 'home':
    home_page()
elif st.session_state['current_page'] == 'student':
    student_page()
elif st.session_state['current_page'] == 'teacher':
    teacher_page()
