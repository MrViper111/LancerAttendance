import smbus2
from adafruit_pn532.i2c import PN532_I2C

pn532 = PN532_I2C(smbus2.SMBus(1))
pn532.SAM_configuration()

key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
block = 4  # Avoid trailer blocks: 3, 7, 11, ...
data = b'Hello NFC!\x00\x00\x00\x00\x00'  # Must be exactly 16 bytes

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
