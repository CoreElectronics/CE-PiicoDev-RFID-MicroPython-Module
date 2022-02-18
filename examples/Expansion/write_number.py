from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

slot = 35
number = 2

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    success = rfid.writeNumber(number, slot=slot)
    if success:
        readNumber = rfid.readNumber(slot=slot)
        print('Number in tag:')
        print(readNumber)
        break
    sleep_ms(10)
