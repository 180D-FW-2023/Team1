import streamlit as st
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
        st.markdown('<a href="/teacher_start" target="_self">Next page</a>', unsafe_allow_html=True)
    with col2:
        st.markdown('<a href="/student_start" target="_self">Next page</a>', unsafe_allow_html=True)

render_home_page()