import os
import cv2
import time
from datetime import datetime
import numpy as np
from typing import List
from threading import Thread, Lock
from datetime import datetime


def image_put_text(image: np.ndarray, text: str, bottom_left_point: List[int]) -> np.ndarray:
    image = cv2.putText(
        img=image,
        text=text,
        org=bottom_left_point,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(0, 0, 0),
        thickness=3
    )
    image = cv2.putText(
        img=image,
        text=text,
        org=bottom_left_point,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),
        thickness=2
    )
    return image


class CameraStream:
    def __init__(self, src=None, add_date=False, fps_counter=False):
        self.src = src
        self.cap = None
        self.init_cap()
        self.add_date = add_date
        self.fps_counter = fps_counter
        self.thread = None
        self.stream_running = False
        self.output = None
        self.lock = Lock()

    def init_cap(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.src)

    def unselect_cap(self):
        self.cap = None

    def set_resolution(self, width, height):
        self.init_cap()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_resolution(self) -> List[int]:
        self.init_cap()
        current_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [current_width, current_height]

    def get_max_resolution(self) -> List[int]:
        """
        https://stackoverflow.com/questions/18458422/query-maximum-webcam-resolution-in-opencv
        """
        high_value = 10000
        current_width, current_height = self.get_resolution()
        self.set_resolution(high_value, high_value)

        max_width, max_height = self.get_resolution()
        self.set_resolution(current_width, current_height)
        return [max_width, max_height]

    def get_frame(self):
        while True:
            with self.lock:
                if self.output is None:
                    continue
                image = self.output.copy()
            flag, image = cv2.imencode('.jpg', image)
            if not flag:
                continue
            yield  b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n'

    def stream_function(self):
        while self.stream_running:
            s = datetime.now()
            ret_val, img = self.cap.read()
            e = datetime.now() - s
            if ret_val:
                if self.add_date:
                    img = image_put_text(img, datetime.now().strftime("%d.%m.%Y %H:%M:%S"), [50, 50])
                if self.fps_counter:
                    img = image_put_text(img, f"fps: {1/e.total_seconds():.2f}", [50, 100])
                with self.lock:
                    self.output = img
            else:
                print(self.src, "error get frame: ")
                time.sleep(1)

    def start(self):
        if not self.stream_running:
            print("start thread")
            self.init_cap()
            self.stream_running = True
            self.thread = Thread(target=self.stream_function, args=())
            self.thread.start()
            print("thread started")

    def stop(self):
        if self.thread is not None:
            print("stop thread")
            self.stream_running = False
            self.thread.join()
            self.unselect_cap()
            print("thread stopped")


def get_available_camera_device(key_index=True):
    devices = [os.path.join("/dev", device) for device in os.listdir("/dev") if "video" in device]

    camera_devices = []
    for device in devices:
        camera_stream = CameraStream(src=device)
        if camera_stream.get_resolution()[0] > 0:
            camera_devices.append(device)

    return camera_devices
