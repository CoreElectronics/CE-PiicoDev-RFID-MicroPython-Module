from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

slot = 35

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    if rfid.tagPresent():
        read_number = rfid.readNumber(slot=slot)
        print('Number in tag:')
        print(read_number)
        sleep_ms(1000)
    sleep_ms(10)