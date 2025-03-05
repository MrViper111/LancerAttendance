import requests
from flask import request

import time
import cv2


cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

while True:
    start_time = time.time()
    ret, frame = cap.read()
    if not ret:
        continue

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:
        print(data.title())
        user_data = requests.get(f"http://127.0.0.1:8000/api/get_user?name={data.title()}").json()
        print(str(user_data))

    cv2.imshow("QR Code Scanner", frame)

    elapsed_time = time.time() - start_time
    time.sleep(max(1.0 - elapsed_time, 0))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()