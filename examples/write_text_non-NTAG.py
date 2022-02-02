from PiicoDev_RFID import *

rfid = PiicoDev_RFID()
register = 8
data = 'Hendrika'
tag_chip = ''
data = '0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'
rfid = PiicoDev_RFID()
adr_list = [1, 2, 4, 5, 6, 8, 9, 10, 12] #16
addr_adr_max = 39 # NTAG213
maximum_characters = 144
tag_chip = ''

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    detect_tag_result = rfid.detectTag()
    tag_present = detect_tag_result['present']
    
    if tag_present:
        read_tag_id_result = rfid.readTagID()
        tag_success = read_tag_id_result['success']
        tag_id = read_tag_id_result['id_formatted']
        buffer_start = 0
        while len(data) < maximum_characters:
            data = data + " "
        if tag_success:
            bytes_per_adr = 16
            x = 0
            for address in adr_list:
                data_chunk = data[buffer_start:buffer_start+bytes_per_adr]
                buffer_start = buffer_start + bytes_per_adr
                print('Data Chunk')
                print(data_chunk)
                data_byte_array = [ord(x) for x in list(data_chunk)]
                print('data_byte_array:')
                print(data_byte_array)
                tag_write_success = rfid.writeTagDataNonNTAG(address, data_byte_array)
            if tag_write_success is True:
                total_string = ''
                for address in adr_list:
                    reg_text= rfid.readTagData(address, 'text', tag_chip)
                    print("ID: ", end=''); print(tag_id)
                    print('Text in register ', end=''); print(register, end=''); print(': ', end=''); print(reg_text)
                    total_string = total_string + reg_text
                    print()
                print('Text on tag: ', end=''); print(total_string)
            break
    sleep_ms(10)