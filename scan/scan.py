import asyncio
import time
import threading
import cv2
import eel
import requests

eel.init("web")

@eel.expose
def set_status(status, name):
    eel.changeStatus(status, name)

# Run Eel in a separate thread
eel_thread = threading.Thread(target=eel.start, args=("index.html",), kwargs={"host": "0.0.0.0"}, daemon=True)
eel_thread.start()

cap = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()
last_scanned = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    try:
        name, points, _ = qr_detector.detectAndDecode(frame)
    except Exception as e:
        print(f"QR Decode Error: {e}")
        name = None

    if name:
        if time.time() - last_scanned <= 3:
            continue
        last_scanned = time.time()

        url = f"http://0.0.0.0:8080/api/get_user?name={name}"
        response = requests.get(url)
        print(name)

        if response.json().get("response") is None:
            print("User does not exist")
            continue

        email = response.json()["response"]["email"]

        url = "http://0.0.0.0:8080/api/check_in"
        data = {"email": email}
        response = requests.get(url, json=data)
        eel.reloadPage()
        time.sleep(0.1)

        name = name.lower().title()
        if response.json().get("response") == "Checked out":
            set_status(-1, name)
        else:
            set_status(1, name)

        time.sleep(3)
        set_status(0, "")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()