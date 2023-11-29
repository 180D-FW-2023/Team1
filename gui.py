import streamlit as st
import cv2
import os
import tempfile
import numpy as np

# Function to convert OpenCV image format to Streamlit format
def opencv_to_streamlit(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Initialize webcam
cap = cv2.VideoCapture(0)
codec = cv2.VideoWriter_fourcc(*'XVID')

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

def teacher_page():
    st.title("Show your students what to do!")
    st.header("Webcam Live Feed")
    recording = False

    # Session state for recording flag and path of the recorded video
    # if 'recording' not in st.session_state:
    #     st.session_state['recording'] = False
    # if 'recorded_video' not in st.session_state:
    #     st.session_state['recorded_video'] = None

    # Button to start/stop recording
    if st.button("Start/Stop Recording"):
        recording = not recording

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output = None

    # Placeholder for the live feed
    frame_holder = st.empty()

    # Continuous loop to update the live feed and handle recording
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the color format for Streamlit
        frame = opencv_to_streamlit(frame)
        frame_holder.image(frame)

        if recording and output is None:
            #setup recording
            output = cv2.VideoWriter('CAPTURE.mp4', codec, 30, (640, 480))
        elif recording and output is not None:
            #write frame
            output.write(frame)
        elif not recording and output is not None:
            #release and save and set output to None
            cap.release()
            output.release()
            output = None
            break
    cap.release()


# Initialize session state for page tracking
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'

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
