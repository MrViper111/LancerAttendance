import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import hashlib

i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
block = 4  # Do not use trailer blocks (3, 7, 11, ...)
data = hashlib.md5("dsachmanyan25".encode()).digest()  # Exactly 16 bytes

print("Place card to write...")

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print("UID:", [hex(x) for x in uid])
        if pn532.mifare_classic_authenticate_block(uid, block, PN532_I2C.MIFARE_CMD_AUTH_A, key):
            success = pn532.mifare_classic_write_block(block, data)
            if success:
                print("Successfully wrote to block", block)
            else:
                print("Write failed.")
        else:
            print("Authentication failed.")
        break
