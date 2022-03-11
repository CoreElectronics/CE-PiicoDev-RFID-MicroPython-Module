# Write a string to a tag, and read it back to show that it wrote correctly

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

myString = 'Hello World!' # You can store up to 143 characters on a tag

print('Hold tag near the PiicoDev RFID Module to write some text to it.')
print('')

while True:
    success = rfid.writeText(myString)
    if success:
        data = rfid.readText()
        print('Text in tag:')
        print(data)
        break
    sleep_ms(10)