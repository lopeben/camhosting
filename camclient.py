import cv2
import time
import platform
import requests
from mysecrets import AWS_ENDPOINT, LOCAL_ENDPOINT


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(4, 720)
        self.video.set(cv2.CAP_PROP_FPS, 120)
        self._last_frame = None # Shared memory

    def __del__(self):
        self.video.release()

    def mirror_frame(self, frame):
        mirrored_frame = cv2.flip(frame, 1)
        return mirrored_frame

    def resize_frame(self, frame, target_width, target_height):
        original_height, original_width = frame.shape[:2]
        aspect_ratio = original_width / original_height
        if target_width / aspect_ratio <= target_height:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        return resized_frame

    def update_frame(self):
        ret, frame = self.video.read()
        resized_frame = self.resize_frame(frame, 640, 480)
        mirrored_frame = self.mirror_frame(resized_frame)
        self._last_frame = mirrored_frame

    def get_frame(self):
        frame = self._last_frame
        print(frame.shape)  # Print out the shape of the frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    

def is_mac():
    return platform.system() == 'Darwin'


def generate(camera):
    while True:
        camera.update_frame()
        frame = camera.get_frame()
        yield frame
        # Send the frame to the endpoint
        if is_mac():
            response = requests.post(LOCAL_ENDPOINT, data=frame)
        else:
            response = requests.post(AWS_ENDPOINT, data=frame)


def main():
    camera = VideoCamera()
    for frame in generate(camera):
        time.sleep(1)


if __name__ == '__main__':
    main()

