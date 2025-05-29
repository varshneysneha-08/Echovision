import cv2
import base64
import time
import requests

def encode_image(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

cap = cv2.VideoCapture(0)
frames = []

for _ in range(3):  # capture 3 frames
    ret, frame = cap.read()
    if ret:
        frames.append(encode_image(frame))
    time.sleep(1 / 3)

response = requests.post("http://127.0.0.1:8000/process-frames/", json={"frames": frames})
print(response.json())
