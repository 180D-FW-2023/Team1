import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Change session state based on page
st.session_state['current_page'] = 'student_start'
if 'received_movement' not in st.session_state:
    st.session_state['received_movement'] = False

def on_recv():
    '''
    convert incoming message to json msg
    if msg['command'] == 'mov':
        # get movement
    '''
    pass

def render_student_start():
    st.title("Welcome to MirrorMe!")
    st.header("Waiting for teacher to send movement")
    if st.button("Exit"):
        # TODO: cleanup mqtt object
        switch_page("home")
    if st.session_state['received_movement']:
        if st.button("Start / Stop"):
            pass

render_student_start()