import cv2

def test_camera():
    # Create a VideoCapture object to access the camera
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera, or change the index if necessary

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Display the frame in a window
        cv2.imshow('Camera Test', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture object and close the window
    cap.release()
    cv2.destroyAllWindows()

# Call the test_camera function to start the camera test
test_camera()
