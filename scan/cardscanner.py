import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import hashlib
import time

# Setup
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

MIFARE_CMD_AUTH_A = 0x60
KEY_DEFAULT = b'\xFF\xFF\xFF\xFF\xFF\xFF'
BLOCK = 4

class CardScanner:

    @staticmethod
    def write_card(input_string):
        print("Place card to write...")

        while True:
            uid = pn532.read_passive_target(timeout=0.5)
            if uid:
                print("UID:", [hex(x) for x in uid])
                if len(uid) != 4:
                    print("This card is not a MIFARE Classic tag. Aborting.")
                    return False

                if not pn532.mifare_classic_authenticate_block(uid, BLOCK, MIFARE_CMD_AUTH_A, KEY_DEFAULT):
                    print("Authentication failed.")
                    return False

                for attempt in range(1, 4):
                    success = pn532.mifare_classic_write_block(BLOCK, input_string)
                    if success:
                        print(f"Successfully wrote to block {BLOCK} on attempt {attempt}")
                        return True
                    else:
                        print(f"Write attempt {attempt} failed.")
                        time.sleep(0.1)

                print("Write failed after 3 attempts.")
                return False

            time.sleep(0.1)

    @staticmethod
    def read_card():
        print("Place card to read...")

        while True:
            uid = pn532.read_passive_target(timeout=0.5)

            if not uid:
                time.sleep(0.1)
                continue

            print("UID:", [hex(x) for x in uid])

            if len(uid) != 4:
                print("This card is not a MIFARE Classic tag. Aborting.")
                return None

            if not pn532.mifare_classic_authenticate_block(uid, BLOCK, MIFARE_CMD_AUTH_A, KEY_DEFAULT):
                print("Authentication failed.")
                return None

            block_data = pn532.mifare_classic_read_block(BLOCK)
            if not block_data:
                print("Read failed.")
                return None

            print("Read success.")

            while pn532.read_passive_target(timeout=0.5):
                time.sleep(0.1)

            return block_data


if __name__ == "__main__":
    action = int(input("Action (read:0, write:1): "))

    if action == 0:
        print(CardScanner.read_card())

    if action == 1:
        card_input = input("String to write: ")
        CardScanner.write_card(card_input)

