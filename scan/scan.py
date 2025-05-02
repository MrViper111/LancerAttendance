import asyncio
import time
import threading
import cv2
import eel
import requests
import numpy as np

eel.init("web")

@eel.expose
def set_status(status, name):
    eel.changeStatus(status, name)

eel_thread = threading.Thread(target=eel.start, args=("index.html",), kwargs={"host": "0.0.0.0"}, daemon=True)
eel_thread.start()

cap = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()
last_scanned = time.time()

while True:
    ret, frame = cap.read()
    print("capturing frame")

    if not ret:
        print("failed to capture frame, OK")
        continue

    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        cv2.imshow("Camera", thresh)
        name, points, _ = qr_detector.detectAndDecode(thresh)
        if not name:
            print("No QR code detected")
    except Exception as e:
        print(f"QR Decode Error: {e}")
        name = None

    if name:
        print(f"Name found: {name}")
        if time.time() - last_scanned <= 3.0:
            continue
        try:
            url = f"http://0.0.0.0:8080/api/get_user?name={name}"
            response = requests.get(url, timeout=2)

            if response.json().get("response") is None:
                print("User does not exist")
                continue
            else:
                print(f"Found user: {name}")

            email = response.json()["response"]["email"]
            url = "http://0.0.0.0:8080/api/check_in"
            data = {"email": email}
            response = requests.post(url, json=data, timeout=2)

            eel.reloadPage()
            time.sleep(0.1)

            name = name.lower().title()
            if response.json().get("response") == "Checked out":
                set_status(-1, name)
            else:
                set_status(1, name)

            last_scanned = time.time()
            time.sleep(3)
            set_status(0, "")
        except:
            continue

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.1)  # so its not like 43294823904 fps

cap.release()
cv2.destroyAllWindows()