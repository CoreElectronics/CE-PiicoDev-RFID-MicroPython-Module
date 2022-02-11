from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    text_read = rfid.readText()
    print('Text in tag:')
    print(text_read)
    break
    sleep_ms(1000)
