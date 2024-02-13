import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import bluetooth
import pandas as pd

# Change session state based on page
if st.session_state.get('message', False):
    st.header(st.session_state['message'])
#st.session_state.clear()
#replacing above statement
for key in st.session_state.keys():
    if key == 'bluetooth_devices' or key == "bluetooth_sock":
        continue
    del st.session_state[key]
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
    data = []
    bluetoothdevices = {}
    nearby_devices = None
    blue_sock = st.session_state["bluetooth_sock"]
    ref_btN = st.button("Refresh")
    if ref_btN:
        st.session_state['bluetooth_devices'] = discover_devices()
    if st.session_state['bluetooth_devices'] != []:
        for addr,name in st.session_state['bluetooth_devices']:
            data.append(name)
            bluetoothdevices[name] = addr
    option = st.selectbox("Choose your Mirror Module!", data, index = None, placeholder = "Select your Mirror Module")
    st.write('You selected:', option)
    if option != None:
        print("Selected")
        print(bluetoothdevices[option])
        blue_sock.connect((bluetoothdevices[option], 1))
        blue_sock.settimeout(0)
        print("Connecting")

    try:
        data = blue_sock.recv(1024)
    except OSError:
        data = ""
    print(data)
    



    


def discover_devices():
    return bluetooth.discover_devices(lookup_names=True)

@st.cache_resource
def bluetoothsock():
    print("Socket created")
    x = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    return x

if 'bluetooth_devices' not in st.session_state:
    st.session_state['bluetooth_devices'] = discover_devices()


if 'bluetooth_sock' not in st.session_state:
    st.session_state['bluetooth_sock'] = bluetoothsock()



render_home_page()