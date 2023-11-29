import numpy as np
import cv2
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import threading
import time

cap = cv2.VideoCapture(0)

FPS = 30
TEST_PATH = []
for i in range(0, 50):
    TEST_PATH.append((50, 100+i*10))
for i in range(0, 100):
    TEST_PATH.append((50+i*10, TEST_PATH[-1][1]))
DRAW_BUFFER = []
CIRCLE_BASE_RADIUS = 25
MAX_BUFFER_SIZE = 40


test_path_ptr = 0
loop_start = time.monotonic_ns()

while(True):
    # Get loop start_time
    loop_start = time.monotonic_ns()
    

    # Get frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Draw path
    # If buffer isn't full and there is still a path to draw
    if len(DRAW_BUFFER) < MAX_BUFFER_SIZE and test_path_ptr < len(TEST_PATH):
        DRAW_BUFFER.append(TEST_PATH[test_path_ptr])
        test_path_ptr += 1
    # If buffer is full and there is still a path to draw
    elif test_path_ptr < len(TEST_PATH):
        DRAW_BUFFER.pop(0)
        DRAW_BUFFER.append(TEST_PATH[test_path_ptr])
        test_path_ptr += 1
    # If path to draw is done, start removing old items
    else:
        DRAW_BUFFER.pop(0)
        if len(DRAW_BUFFER) == 0:
            test_path_ptr = 0
    for (x, y), i in zip(DRAW_BUFFER, range(len(DRAW_BUFFER), -1, -1)):
        cv2.circle(frame, center=(x,y), radius=CIRCLE_BASE_RADIUS-i//2, color=(255, i*5, i*5), thickness=-1)

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