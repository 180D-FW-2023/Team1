import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Change session state based on page
st.session_state['current_page'] = 'student_start'

# TODO: mqtt: - become main publisher of teacher_room_code
#             - subscibe to student_room_code

def on_recv():
    '''
    convert incoming message to json msg
    if msg['command'] == 'start:
        switch_page('student_perform')
    '''
    pass

def render_student_start():
    st.title("Welcome to MirrorMe!")
    name = st.text_input(
        "Enter Name:",
        placeholder = "Name"
    )
    room_code = st.text_input(
        "Enter Room Code:",
        placeholder = "Room Code"
    )
    if room_code:
        st.session_state['room_code'] = room_code
        st.header(f"Joined Room: {st.session_state['room_code']}")
    st.header(" ")
    if st.button("Exit"):
        # TODO: cleanup mqtt object
        # send exit message to teacher
        switch_page("home")

render_student_start()