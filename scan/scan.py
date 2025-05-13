import time
import threading
import eel
import requests
import os

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
        "mode": "/snap/bin/chromium",
        "cmdline_args": [
            "--kiosk",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer"
        ]
    },
    daemon=True
)

eel_thread.start()
time.sleep(1)

last_scanned = 0

while True:
    cards = requests.get("http://0.0.0.0:8080/api/get_cards").json()["response"]
    print(cards)

    card_value = CardScanner.read_card()
    if card_value:
        print("found", str(card_value))

        card_data = None
        for i, card in enumerate(cards):
            if card["id"] == card_value:
                card_data = cards[i]

        if not card_data or not card_data["enabled"]:
            continue

        print("ok, finding user data")
        user_data = requests.get("http://localhost:8080/api/get_user", params={"id": card_value["user_id"]}).json()

        url = "http://0.0.0.0:8080/api/check_in"
        data = {"id": user_data["name"]}
        response = requests.post(url, json=data).json()

        if response["response"] == "Checked out":
            set_status(-1, user_data["name"])
        else:
            set_status(1, user_data["name"])

        time.sleep(3)
        set_status(0, "")
        eel.reloadPage()
