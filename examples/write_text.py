from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

text = '0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    success = rfid.writeTextToTag(text)
    if success:
        text_read = rfid.readTextFromTag()
        print('Text in tag:')
        print(text_read)
        break
    sleep_ms(10)