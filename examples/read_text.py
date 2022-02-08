from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    text_read = rfid.readTextFromTag()
    print('Text in tag:')
    print(text_read)
    break
    sleep_ms(1000)
