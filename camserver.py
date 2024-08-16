import os
import cv2
import time
import logging
import platform
import numpy as np


# from PIL import Image
from flask import Flask, request
from flask_socketio import SocketIO
from flask import Flask, Response, stream_with_context, render_template


app = Flask(__name__)


# Setting a random secret key for the Flask application
app.config['SECRET_KEY'] = os.urandom(24)
app.logger.setLevel(logging.INFO)


def is_mac():
    return platform.system() == 'Darwin'

if is_mac():
    socketio = SocketIO(app) # Use this when debugging in mac
else:
    socketio = SocketIO(app, async_mode='gevent', logger=True, engineio_logger=True)


# This function will store the processed frame in a file
def store_frame(jpeg_frame):
    with open('frame.jpg', 'wb') as f:
        f.write(jpeg_frame)


# This function will retrieve the processed frame from the file
def retrieve_frame():
    with open('frame.jpg', 'rb') as f:
        return f.read()


@app.route('/receive_endpoint', methods=['POST'])
def receive_frame():
    frame_data = request.data
    nparr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert the frame to RGB color (from BGR)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    ret, jpeg = cv2.imencode('.jpg', frame)
    jpeg_frame = jpeg.tobytes()

    # Store the processed frame
    store_frame(jpeg_frame)

    return {"status": "Frame received and processed"}


@app.route('/video_stream')
def video_stream():
    def generate_frame():
        while True:
            # Retrieve the processed frame
            jpeg_frame = retrieve_frame()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n')

    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/image_feed')
def image_feed():
    def generate_frame():
        last_frame = None
        while True:
            # Retrieve the processed frame
            jpeg_frame = retrieve_frame()

            # If the frame has changed, yield it
            if jpeg_frame != last_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n')
                last_frame = jpeg_frame

            # Sleep for a while to reduce CPU usage
            time.sleep(0.1)

    return Response(stream_with_context(generate_frame()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('stream.html')


if __name__ == '__main__':
    # app.run(debug=True)
    if is_mac():
        # Debug setting WSGI
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    else:
        # Production setting WSGI
        socketio.run(app, debug=False, host='0.0.0.0', port=80)


