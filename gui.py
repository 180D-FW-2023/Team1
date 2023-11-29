import streamlit as st
import cv2
import os
import tempfile
import numpy as np
import speech_recognition as sr
import threading
#import pyttsx3

# Function to convert OpenCV image format to Streamlit format
def opencv_to_streamlit(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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

def callback(recognizer, audio):                          # this is called from the background thread
    try:
        ans = recognizer.recognize_google(audio)
        print("You said " + ans)  # received audio data, now need to recognize it
        if ans == 'start':
            st.session_state['start'] = 1
        else:
            st.session_state['start'] = 0
        if ans == 'stop':
            st.session_state['stop'] = 1
        else:
            st.session_state['stop'] = 0
    except sr.RequestError:
        print("Google not available") 
    except sr.UnknownValueError:
        print("Can't understand")



def teacher_page():
    st.title("Show your students what to do!")
    st.header("Webcam Live Feed")
    recording = False
    r = sr.Recognizer()
    r.listen_in_background(sr.Microphone(), callback)
    
    # Session state for recording flag and path of the recorded video
    # if 'recording' not in st.session_state:
    #     st.session_state['recording'] = False
    # if 'recorded_video' not in st.session_state:
    #     st.session_state['recorded_video'] = None
    # Button to start/stop recording
    container_2 =  st.empty()
    container_3 = st.empty()
    start_btN = container_2.button("Start Recording")
    recording = 0
    if os.path.isfile("CAPTURE.mp4"):
            video_file = open('CAPTURE.mp4','rb')
            video_bytes = video_file.read()
            frame_holder = container_3.video(video_bytes)
    if start_btN or st.session_state['start'] or st.session_state['stop']:
        container_2.empty()
        end_btN = container_2.button("Stop Recording")
        frame_holder = container_3.empty()
        recording = 1
  



    # Initialize webcam
    
    cap = cv2.VideoCapture(0)
    codec = cv2.VideoWriter_fourcc(*'H264') #mp4v doesn't work
    output = None

        


    # Continuous loop to update the live feed and handle recording
    if start_btN:
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
                output.write(opencv_to_streamlit(frame))
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
if 'start' not in st.session_state:
    st.session_state['start'] = 0
if 'stop' not in st.session_state:
    st.session_state['stop'] = 0

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
