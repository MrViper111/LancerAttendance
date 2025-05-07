import board
import busio
from adafruit_pn532.i2c import PN532_I2C

i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
block = 4  # Block to read (avoid sector trailers like 3, 7, 11, etc.)

print("Place card to read block", block)

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print("UID:", [hex(x) for x in uid])
        if pn532.mifare_classic_authenticate_block(uid, block, PN532_I2C.MIFARE_CMD_AUTH_A, key):
            data = pn532.mifare_classic_read_block(block)
            print("Block", block, "data:", data)
        else:
            print("Authentication failed.")
        break
