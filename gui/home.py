import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Change session state based on page
st.session_state.clear()
st.session_state['current_page'] = 'home'

def render_home_page():
    st.title("Welcome to MirrorMe!")
    st.header("Join As:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Teacher"):
            switch_page("teacher_start")
    with col2:
        if st.button("Student"):
            switch_page("student_start")

render_home_page()