# Read a number from a tag and do some simple math
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Hold tag near the PiicoDev RFID Module to read a number')
print('')

while True:
    if rfid.tagPresent():
        data = rfid.readNumber(slot=0) # read a number from slot0
        print('Number in tag: ' + str(data))
        newData = data + 1 # it's a real number, we can use it for math and stuff!
        print(str(data) +' plus 1 is '+ str(newData))
        sleep_ms(1000)
    sleep_ms(10)