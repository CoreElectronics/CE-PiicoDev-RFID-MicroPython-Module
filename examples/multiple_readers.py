from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

readerA = PiicoDev_RFID(suppress_warnings=True)                 # Initialise the first RFID module as reader A with default address 0x2D
readerB = PiicoDev_RFID(address=0x2D, suppress_warnings=True)     # Initialise the second RFID module as reader B

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
