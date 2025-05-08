import time
import threading
import eel
import requests

from cardscanner import CardScanner

eel.init("web")

@eel.expose
def set_status(status, name):
    eel.changeStatus(status, name)

def start_eel():
    eel.start("index.html", host="0.0.0.0", block=False)

eel_thread = threading.Thread(target=start_eel, daemon=True)
eel_thread.start()

last_scanned = 0

while True:
    if CardScanner.read_card():
        print("found")

        eel.spawn(set_status, 1, "something???")
        eel.spawn(eel.reloadPage)

        time.sleep(1)

        eel.spawn(set_status, 0, "")
