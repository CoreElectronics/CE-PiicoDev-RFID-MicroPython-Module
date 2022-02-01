from PiicoDev_RFID import *

rfid = PiicoDev_RFID()
register = 8
data = 'Hendrika'
#tag_chip = ''
tag_chip = 'NTAG2xx'

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    detect_tag_result = rfid.detectTag()
    tag_present = detect_tag_result['present']
    
    if tag_present:
        read_tag_id_result = rfid.readTagID()
        tag_success = read_tag_id_result['success']
        tag_id = read_tag_id_result['id_formatted']
        print(tag_id)
 
        if tag_success:
            data_byte_array = ([3, 4, 5, 6])
            print(data_byte_array)
            stat = rfid.nTAG2xxWrite(8, data_byte_array)
            #tag_write_success = rfid.writeTagData(data, register, tag_chip)
            if tag_write_success is True:
                tag_text= rfid.readTagData(register, 'text', tag_chip)
                print("ID: ", end=''); print(tag_id)
                print('Text in register ', end=''); print(register, end=''); print(': ', end=''); print(tag_text)
                print()
            break
    sleep_ms(10)
