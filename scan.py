import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import hashlib
import time

# Setup
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

# Constants
MIFARE_CMD_AUTH_A = 0x60
key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
block = 4  # Avoid trailer blocks
data = hashlib.md5("dsachmanyan25".encode()).digest()  # 16 bytes

print("Place card to write...")

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print("UID:", [hex(x) for x in uid])
        if len(uid) != 4:
            print("This card is not a MIFARE Classic tag. Aborting.")
            break
        try:
            # Authenticate
            if pn532.mifare_classic_authenticate_block(uid, block, MIFARE_CMD_AUTH_A, key):
                # Write
                success = pn532.mifare_classic_write_block(block, data)
                if success:
                    print("Successfully wrote to block", block)
                else:
                    print("Write failed.")
            else:
                print("Authentication failed.")
        except RuntimeError as e:
            print(f"Operation failed: {e}")
        break
    time.sleep(0.1)
