# Read a string from a tag.

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Hold tag near the PiicoDev RFID Module to read some text')
print('')

while True:
    myString = rfid.readText()
    print('Text in tag:')
    print(myString)
    break
    sleep_ms(1000)
