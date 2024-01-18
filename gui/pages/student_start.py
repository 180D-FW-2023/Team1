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
st.session_state.update(st.session_state)
st.write(st.session_state)
st.session_state['current_page'] = 'student_start'
st.header("student_page")
st.markdown('<a href="/teacher_start" target="_self">Next page</a>', unsafe_allow_html=True)