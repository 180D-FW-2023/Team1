import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_lottie import st_lottie
import pandas as pd

# Change session state based on page
if st.session_state.get('message', False):
    st.header(st.session_state['message'])
st.session_state.clear()
st.session_state['current_page'] = 'home'

with open('gui/style.css') as f:    
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_home_page():
    col1, col2 = st.columns([2, 10])
    with col1:
        st_lottie('https://lottie.host/edb12174-1102-4fc5-a7b7-e695bf7b52c2/ui94YFdvMi.json', key="user")
    with col2:
        st.title("Welcome to MirrorMe!")
    # st.markdown('''<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">''', unsafe_allow_html=True)
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([5.2, 5, 5])
        with col2:
            st.header("Join As:")
        col1, col2, col3, col4 = st.columns([1.7,2.5,2.5,2])
        with col2:
            if st.button("Teacher", use_container_width=True):
                switch_page("teacher_start")
        with col3:
            if st.button("Student", use_container_width=True):
                switch_page("student_start")

render_home_page()
