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
        print('Reader A ID: ' + str(id))  # print the id
        
    if readerB.tagPresent():              # if an RFID tag is present on reader B
        id = readerB.readID()             # get the id
        print('Reader B ID: ' + str(id))  # print the id

    sleep_ms(500)
