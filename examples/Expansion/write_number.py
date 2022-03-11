# Write a number to a tag. Numbers must be integers between −2,147,483,647, +2,147,483,647
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Hold tag near the PiicoDev RFID Module to write a number')
print('')

while True:
    success = rfid.writeNumber(123456, slot=0) # Write a number to slot0. There are 36 slots available (0-35) to store numbers/text
    if success:
        data = rfid.readNumber(slot=0) # Read back from slot0
        print('Number in tag:')
        print(data)
        break
    sleep_ms(10)
