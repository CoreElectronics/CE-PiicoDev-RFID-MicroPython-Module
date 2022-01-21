from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    detect_tag_result = rfid.detectTag()
    tag_present = detect_tag_result['present']
    
    if tag_present:
        read_tag_id_result = rfid.readTagID()
        tag_success = read_tag_id_result['success']
        tag_id = read_tag_id_result['id_formatted']
 
        if tag_success:
            print("ID: ", end=''); print(tag_id)
            sleep_ms(1000)
    sleep_ms(10)
    
