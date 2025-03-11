import cv2
import time
import requests
import threading


def scan_qr_code():
    cap = cv2.VideoCapture(0)
    qr_detector = cv2.QRCodeDetector()
    last_scanned = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        try:
            name, points, _ = qr_detector.detectAndDecode(frame)
        except:
            pass

        if name:
            if time.time() - last_scanned <= 3:
                continue
            last_scanned = time.time()

            url = f"http://0.0.0.0:8080/api/get_user?name={name}"
            response = requests.get(url)
            print(name)

            if response.json()["response"] is None:
                print("User does not exist")
                continue

            email = response.json()["response"]["email"]

            url = "http://0.0.0.0:8080/api/check_in"
            data = {"email": email}
            response = requests.get(url, json=data)
            print(response.json())

            if response.json()["response"] == "Checked out":
                print(f"Checked out: {name}")
            else:
                print(f"Check-in successful: {name}")

        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    scan_qr_code()