import numpy as np
import cv2
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import threading
import time
from model_utils import *
import movement
import bluetooth

cap = cv2.VideoCapture(0)
server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
print("Waiting for connection on RFCOMM channel", port)
client_sock,address = server_sock.accept()
print("Accepted connection from ",address)
client_sock.settimeout(0)

FPS = 24

time_start = time.monotonic_ns()
record_mode = True
mov = movement.Movement()

while(True):
    # Get loop start time
    loop_start = time.monotonic_ns()
    try:
        data = client_sock.recv(1024)
    except OSError:
        data = None

    # Get frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # For testing, after 10 seconds, set to display mode
    if record_mode and time.monotonic_ns() > time_start + (5*1_000_000_000):
        record_mode = False
        print("Entering display mode")

    # In recording mode, add points to movement object
    if record_mode:
        new_points = StickFigureEstimator.generate_points(frame)
        frame = StickFigureEstimator.overlay_points(frame, new_points)
        if data != None:
            new_points[movement.Movement.POINT_JUMP] = True # TODO: get jump bool from IMU
        else:
            new_points[movement.Movement.POINT_JUMP] = False

        mov.add_captured_points(new_points)
    
    # In draw mode, get next frame of movement display
    else:
        if mov.is_done():
            s = mov.get_movement_json()
            mov.reset()
            mov = movement.Movement(s)
        frame = mov.display_and_advance_frame(frame)

    # Display frame
    cv2.imshow('RGB', frame)

    # Check for exit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Ensure consistent time between frames of 1/FPS seconds
    while time.monotonic_ns() < loop_start + (1/FPS*1_000_000_000):
        pass

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
