import cv2
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time
import requests
from tkinterweb import HtmlFrame  # import the HtmlFrame widget


class QRScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lancer Attendance")
        self.root.geometry("1920x1080")
        frame = HtmlFrame(self.root)  # create the HTML widget
        frame.load_website("http://tkhtml.tcl.tk/tkhtml.html")  # load a website
        frame.pack(fill="both", expand=True)  # attach the HtmlFrame widget to the window

        self.root.after(0, self.show_scanner_screen)

        self.running = True
        self.last_scanned = time.time()
        threading.Thread(target=self.scan_qr_code, daemon=True).start()

    def scan_qr_code(self):
        cap = cv2.VideoCapture(0)  # Open webcam
        qr_detector = cv2.QRCodeDetector()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            # Detect QR Code
            name, points, _ = qr_detector.detectAndDecode(frame)

            if name:
                # Prevent multiple rapid scans
                if time.time() - self.last_scanned <= 3:
                    continue
                self.last_scanned = time.time()

                url = f"http://10.200.86.204:8000/api/get_user?name={name}"  # replace with your endpoint
                response = requests.get(url)
                print(name)

                if response.json()["response"] is None:
                    print("user does not exist")
                    continue

                email = response.json()["response"]["email"]

                url = "http://10.200.86.204:8000/api/check_in"  # replace with your endpoint
                data = {"email": email}
                response = requests.get(url, json=data)  # use `json=data` for JSON payload or `data=data` for form data
                print(response.json())

                if response.json()["response"] == "Checked out":
                    self.root.after(0, self.show_checkout_screen, name)
                else:
                    self.root.after(0, self.show_checkmark_screen, name)  # Show checkmark screen

                self.root.after(3000, self.show_scanner_screen)  # Pause before returning to scanning

            elif not name:
                self.root.after(0, self.update_label, "Waiting for QR Code...")  # Reset UI when no QR detected

            cv2.waitKey(1)  # Prevents excessive CPU usage

        cap.release()

    def update_label(self, text):
        """Update the UI label dynamically"""
        self.result_label.config(text=text, bootstyle="success" if text != "Waiting for QR Code..." else "secondary")

    def show_checkmark_screen(self, data):
        """Display checkmark screen after scanning QR"""
        for widget in self.root.winfo_children():
            widget.destroy()  # Clear current UI

        check_icon = tb.Label(self.root, text="✓", font=("Arial", 50), bootstyle="success")
        check_icon.pack(pady=20)

        scanned_label = tb.Label(self.root, text=f"Scanned: {data}", font=("Arial", 14), bootstyle="success")
        scanned_label.pack(pady=10)

    def show_checkout_screen(self, data):
        """Display Checkout screen after scanning QR"""
        for widget in self.root.winfo_children():
            widget.destroy()  # Clear current UI

        checkout_icon = tb.Label(self.root, text="🖐️", font=("Arial", 50), bootstyle="warning")
        checkout_icon.pack(pady=20)

        scanned_label = tb.Label(self.root, text=f"Checked out: {data}", font=("Arial", 14), bootstyle="warning")
        scanned_label.pack(pady=10)

    def show_scanner_screen(self):
        """Return to scanning mode"""
        for widget in self.root.winfo_children():
            widget.destroy()  # Clear checkmark screen

        self.label = tb.Label(self.root, text="Scan a QR Code", font=("Arial", 100), bootstyle="primary")
        self.label.pack(pady=20)

        self.result_label = tb.Label(self.root, text="Waiting for QR Code...", font=("Arial", 12),
                                     bootstyle="secondary")
        self.result_label.pack(pady=10)


# Run the application
if __name__ == "__main__":
    root = tb.Window(themename="superhero")  # Modern UI theme
    app = QRScannerApp(root)
    root.mainloop()