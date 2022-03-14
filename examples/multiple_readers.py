# Read from two RFID modules independently
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

readerA = PiicoDev_RFID(asw=[0,0])     # Initialise the first RFID module with both address switches OFF
readerB = PiicoDev_RFID(asw=[1,0])     # Initialise the second RFID module with the first address switch ON

print('Place tag near one of the PiicoDev RFID Modules')
print('')

while True:    
    if readerA.tagPresent():              # if an RFID tag is present on reader A
        id = readerA.readID()             # get the id
        print('RFID A: ' + id)            # print the id on the left side of the shell
        
    if readerB.tagPresent():              # if an RFID tag is present on reader B
        id = readerB.readID()             # get the id
        print(30*' ' + 'RFID B: ' + id)   # print the id on the right side of the shell

    sleep_ms(500)
