import asyncio
import time
import threading
import cv2
import eel
import requests
import numpy as np

import scan.scan

from scan import CardScanner

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

    if CardScanner.read_card():
        print("found")
        set_status(1, "something???")
        eel.reloadPage()
        time.sleep(1)
        set_status(0, "")



        # url = f"http://0.0.0.0:8080/api/get_user?name={name}"
        # response = requests.get(url)

        # if response.json().get("response") is None:
        #     print("User does not exist")
        #     continue
        # else:
        #     print(f"Found user: {name}")

        # email = response.json()["response"]["email"]
        # url = "http://0.0.0.0:8080/api/check_in"
        # data = {"email": email}
        # response = requests.post(url, json=data)
        #
        # eel.reloadPage()
        # time.sleep(0.1)
        #
        # name = name.lower().title()
        # if response.json().get("response") == "Checked out":
        #     set_status(-1, name)
        # else:
        #     set_status(1, name)

        # set_status(0, "")