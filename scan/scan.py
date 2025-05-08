import time
import threading
import eel
import requests

from cardscanner import CardScanner

eel.init("web")

@eel.expose
def set_status(status, name):
    eel.changeStatus(status, name)

eel_thread = threading.Thread(target=eel.start, args=("index.html",), kwargs={"host": "0.0.0.0"}, daemon=True)
eel_thread.start()
time.sleep(1)

last_scanned = 0

while True:
    users = requests.get("http://0.0.0.0:8080/api/get_users").json()["response"]
    hashed_ids = [CardScanner.hash_str(user["id"]) for user in users]

    print(users)
    print(hashed_ids)

    card_value = CardScanner.read_card()
    if card_value:
        print("found", str(card_value))

        user_data = None
        for i, hashed_id in enumerate(hashed_ids):
            if hashed_id == card_value:
                user_data = users[i]

        if not user_data:
            break

        url = "http://0.0.0.0:8080/api/check_in"
        data = {"id": user_data["id"]}
        response = requests.post(url, json=data).json()

        print("RESPONSE", response)

        if response.get("response") == "Checked out":
            set_status(-1, user_data["name"])
        else:
            set_status(1, user_data["name"])

        eel.reloadPage()

        time.sleep(3)
        set_status(0, "")
