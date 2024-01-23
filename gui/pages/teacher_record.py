import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Change session state based on page
st.session_state['current_page'] = 'teacher_record'
st.session_state['movement_recorded'] = False

# TODO: mqtt: - become main publisher of teacher_room_code
#             - subscibe to student_room_code

def on_recv():
    '''
    convert incoming message to json msg
    if msg['command'] == 'exit':
        st.session_start['students'].remove(msg['name'])
    elif msg['command'] == 'score':
        st.session_start['students'].update({msg['name']: msg['score']})
    '''
    pass

def render_teacher_record():
    st.title("Record your Movement for your Students!")
    st.header(" ")
    st.header("Students:" )
    if st.button("Exit"):
        st.session_state['pub'].loop_stop()
        st.session_state['pub'].disconnect()
        switch_page("home")
    recording_button = st.empty()
    recording_button.button('Record')
    if st.button("Send"):
        st.session_state['pub'].publish('ece180d/test', "joe", qos=1)
        recording_button.empty()
        recording_button.button('Rerecord')
        st.session_state['movement_recorded'] = True

render_teacher_record()