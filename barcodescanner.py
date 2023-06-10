import cv2
from pyzbar import pyzbar


def generate_frames():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        if not ret:
            break

        # Detect barcodes in the frame
        frame_with_barcode = detect_barcode(frame)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame_with_barcode)

        # Yield the byte stream for displaying the frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    # Release the camera
    cap.release()
def detect_barcode(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect barcodes in the frame
    barcodes = pyzbar.decode(gray)

    # Loop over the detected barcodes
    for barcode in barcodes:
        # Extract the bounding box coordinates and barcode data
        (x, y, w, h) = barcode.rect
        barcode_data = barcode.data.decode("utf-8")

        # Draw a rectangle around the barcode
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Put the barcode data as text on the frame
        cv2.putText(frame, barcode_data, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)