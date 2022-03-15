from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
import music

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

# A list of authorised users. Add your tag ID as a string to this list. eg: authorised_users = ['##:##:##:##:##:##:##'] 
authorised_users = [''] 

while True:
    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
        print(id)            # print the id
 
        if id in authorised_users:  # check if the tag is in the authorised-user list
            print('Access Granted!\n')
            music.play(music.BA_DING)
            # Your code here for authorised users
            
        else:
            print('*** ACCESS DENIED ***\n')
            sadTune = ["D#","C"] # a descending tone
            music.play(sadTune)
            # Your code here for unauthorised users
            
        sleep_ms(1000)
    sleep_ms(10)