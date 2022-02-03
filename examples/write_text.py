from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

# The maximum number of characters in text is 144
text = 'cdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    success = rfid.writeTextToTag(text)
    if success:
        print('The tag now has the following string:')
        text = rfid.readTextFromTag()
        print(text)
        break
    sleep_ms(10)
