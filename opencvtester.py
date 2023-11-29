import cv2

# Initialize video capture
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object - using H.264 (may need to adjust based on your system)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

recording = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Start/stop recording on pressing 'r'
    if cv2.waitKey(1) & 0xFF == ord('r'):
        recording = not recording

    if recording:
        # Write the frame to file
        out.write(frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything when done
cap.release()
out.release()
cv2.destroyAllWindows()
