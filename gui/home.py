import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import cv2
import os
import numpy as np
import threading
import time

# Hide the sidebar
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for page tracking
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'

def render_home_page():
    st.title("Welcome to MirrorMe!")
    st.header("Join As:")
    col1, col2 = st.columns(2)
    st.write(st.session_state)
    with col1:
        # Pass a function reference and arguments
        st.button("Teacher", on_click=switch_page, args=('teacher_start',))
    with col2:
        st.button("Student", on_click=switch_page, args=('student_start',))

render_home_page()