from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

# The maximum number of characters in text is 144
text = 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    success = rfid.writeTextToClassic(text)
    if success:
        print('The tag now has the following string:')
        print(rfid.readTextFromClassic())
        break
    sleep_ms(10)