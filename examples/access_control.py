from PiicoDev_RFID import *

authorised_ids_filename = 'authorised_ids.txt'

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

# Read the Authorised ID file
f = open(authorised_ids_filename, 'r')
authorised_ids_file_content = f.read()
authorised_ids = authorised_ids_file_content.split('\n')
for i in range(0,len(authorised_ids)):
    authorised_ids[i] = authorised_ids[i].strip()

while True:
    access_granted = False
    
    detect_tag_result = rfid.detectTag()
    tag_present = detect_tag_result['present']
    
    if tag_present:
        read_tag_id_result = rfid.readTagID()
        tag_success = read_tag_id_result['success']
        tag_id = read_tag_id_result['id_formatted']
 
        if tag_success:
            for i in range(0, len(authorised_ids)):
                if tag_id == authorised_ids[i]:
                    access_granted = True
        if access_granted is True:
            print('Access GRANTED')
        else:
            print('Access DENIED')
        sleep_ms(1000)
    sleep_ms(10)