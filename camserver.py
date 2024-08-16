import os
import cv2
import logging
import platform
import numpy as np


# from PIL import Image
from flask import Flask, request
from flask_socketio import SocketIO
from flask import Flask, render_template, Response


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


@app.route('/video_feed')
def video_feed():
    def generate_frame():
        while True:
            # Retrieve the processed frame
            jpeg_frame = retrieve_frame()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n')

    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    # app.run(debug=True)
    if is_mac():
        # Debug setting WSGI
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    else:
        # Production setting WSGI
        socketio.run(app, debug=False, host='0.0.0.0', port=80)



















# from flask import Flask, request
# import cv2
# import numpy as np

# app = Flask(__name__)

# @app.route('/receive_frame', methods=['POST'])
# def receive_frame():
#     frame_data = request.data
#     nparr = np.fromstring(frame_data, np.uint8)
#     frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # Write the frame to a file
#     cv2.imwrite('received_frame.jpg', frame)

#     return {"status": "Frame received and saved"}

# if __name__ == '__main__':
#     app.run(debug=True)

