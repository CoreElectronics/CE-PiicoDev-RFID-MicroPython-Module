from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

text = '0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'
#text = 'https://piico.dev/p16'
#text = 'a'

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    success = rfid.writeText(text)
    if success:
        text_read = rfid.readText()
        print('Text in tag:')
        print(text_read)
        break
    sleep_ms(10)