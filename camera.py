import cv2
from model_utils import generate_points, overlay_points

counter = 0
# Create a VideoCapture object to capture video from the default camera
cap = cv2.VideoCapture(0)

# Loop over frames from the video stream
while True:
    # Read a frame from the video stream
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # If the frame was not successfully read, break out of the loop
    if not ret:
        break

    # Generate pose estimation points
    points = generate_points(frame)
    # Display the frame in a window
    frame = overlay_points(frame, points)

    cv2.imshow('frame', frame)

    # Wait for a key press and check if the 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    counter += 1

# Release the VideoCapture object and close the window
cap.release()
cv2.destroyAllWindows()

