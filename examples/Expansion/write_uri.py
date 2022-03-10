from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

uri = 'https://piico.dev/p16'

while True:
    if rfid.tagPresent():
        success = rfid.writeLink(uri)
        if success:
            print('Write successful')
            break
    sleep_ms(10)
