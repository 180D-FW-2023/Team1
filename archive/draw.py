import numpy as np
import cv2
import threading
import time
from model_utils import *
import movement
from point import *

cap = cv2.VideoCapture(0)


FPS = 24

time_start = time.monotonic_ns()
record_mode = True
mov = movement.Movement()

last_seen = {x: None for x in range(17)}
while(True):
    # Get loop start time
    loop_start = time.monotonic_ns()

    # Get frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # For testing, after 10 seconds, set to display mode
    if record_mode and time.monotonic_ns() > time_start + (20*1_000_000_000):
        record_mode = False
        print("Entering display mode")

    # In recording mode, add points to movement object
    if record_mode:
        new_points = StickFigureEstimator.generate_points(frame)
        for key, val in new_points.items():
            if val == None:
                new_points[key] = last_seen[key]
            else:
                last_seen[key] = val
                
        frame = StickFigureEstimator.overlay_avatar(frame, new_points)

        if None != None:
            new_points[POINT_JUMP] = True # TODO: get jump bool from IMU
        else:
            new_points[POINT_JUMP] = False

        mov.add_captured_points(new_points)
    
    # In draw mode, get next frame of movement display
    else:
        if mov.is_done():
            s = mov.get_movement_json()
            mov.reset()
            mov = movement.Movement(s)
        new_points[POINT_JUMP] = False
        current_points = StickFigureEstimator.generate_points(frame)
        current_points[POINT_JUMP] = False
        frame = mov.display_and_advance_frame(frame, current_points)

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

