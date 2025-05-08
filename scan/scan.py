import time
import threading
import eel
import requests

from cardscanner import CardScanner

eel.init("web")

@eel.expose
def set_status(status, name):
    eel.changeStatus(status, name)

eel_thread = threading.Thread(
    target=eel.start,
    args=("index.html",),
    kwargs={
        "host": "0.0.0.0",
        "port": 8000,
        "mode": "chrome",
        "cmdline_args": ["--start-fullscreen"]
    },
    daemon=True
)
eel_thread.start()

time.sleep(2)

last_scanned = 0

while True:
    if CardScanner.read_card():
        print("found")

        set_status(1, "something???")
        eel.reloadPage()

        time.sleep(1)

        set_status(0, "")
