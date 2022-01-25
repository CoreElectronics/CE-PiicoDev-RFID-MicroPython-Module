from PiicoDev_RFID import *

rfid = PiicoDev_RFID()
register = 8
data = 'Hendrika'

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
            tag_write_success = rfid.writeTagData(data, register)
            if tag_write_success is True:
                print('Data written to tag')
                tag_text = rfid.readTagData(register, 'text')
                print("ID: ", end=''); print(tag_id)
                print('Text in register ', end=''); print(register, end=''); print(': ', end=''); print(tag_text)
                print()
                break
            sleep_ms(1000)
    sleep_ms(10)
