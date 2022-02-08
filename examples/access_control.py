from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

# Read the Authorised ID file
authorised_users = ['04:F2:0A:D2:ED:6C:84']

while True:
    access_granted = False
    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readId()   # get the id
        print(id)            # print the id
 
        if id in authorised_users:
            print('access granted')
        else:
            print('access denied')
        sleep_ms(1000)
    sleep_ms(10)