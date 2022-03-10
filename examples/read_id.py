from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
#         id = rfid.readID(detail=True) # gets more details eg. tag type

        print(id)            # print the id

    sleep_ms(100)
