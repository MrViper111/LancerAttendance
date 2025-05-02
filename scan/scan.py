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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
qr_detector = cv2.QRCodeDetector()
last_scanned = time.time()
cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Processed", 640, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("failed to capture frame, OK")
        continue

    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
        sharpened = cv2.addWeighted(equalized, 1.5, blurred, -0.5, 0)
        processed = cv2.resize(sharpened, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    except Exception as e:
        print(f"QR Decode Error: {e}")
        processed = None

    if processed is not None:
        if time.time() - last_scanned < 3:
            cv2.imshow("Processed", processed)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        name, points, _ = qr_detector.detectAndDecode(processed)
        if points is not None:
            pts = points[0].astype(int)
            x, y, w, h = cv2.boundingRect(pts)
            cv2.rectangle(processed, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if not name:
            print("No QR code detected")
        else:
            print(f"Name found: {name}")
            try:
                url = f"http://0.0.0.0:8080/api/get_user?name={name}"
                response = requests.get(url, timeout=2)

                if response.json().get("response") is None:
                    print("User does not exist")
                    continue
                else:
                    print(f"Found user: {name}")

                last_scanned = time.time()

                email = response.json()["response"]["email"]
                url = "http://0.0.0.0:8080/api/check_in"
                data = {"email": email}
                response = requests.post(url, json=data)

                eel.reloadPage()
                time.sleep(0.1)

                name = name.lower().title()
                if response.json().get("response") == "Checked out":
                    set_status(-1, name)
                else:
                    set_status(1, name)

                set_status(0, "")
            except:
                continue

    if processed is not None:
        cv2.imshow("Processed", processed)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.2)  # so its not like 43294823904 fps

cap.release()
cv2.destroyAllWindows()