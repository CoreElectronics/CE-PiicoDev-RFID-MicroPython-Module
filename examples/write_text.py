from PiicoDev_RFID import *

rfid = PiicoDev_RFID()
page_adr_min = 4 # user memory is 4 to 39 for NTAG213 so that allows for 212 characters.  So that's 36 pages
page_adr_max = 39 # NTAG213
maximum_characters = 144
bytes_per_page = 4
data = '0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMN'
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
        buffer_start = 0
        while len(data) < maximum_characters:
            data = data + " "
        if tag_success:
            #stat = rfid.nTAG2xxWrite(40, [0, 0, 0, 0]) # Attempt to unlock the lock bytes
            bytes_per_page = 4
            page_adr = page_adr_min
            while(page_adr <= page_adr_max):
                data_chunk = data[buffer_start:buffer_start+bytes_per_page]
                print('Data Chunk')
                print(data_chunk)
                buffer_start = buffer_start + bytes_per_page
                #data_encoded = data.encode()
                data_byte_array = [ord(x) for x in list(data_chunk)]
                print('data_byte_array:')
                print(data_byte_array)
                print('Data in page ', end=''); print(page_adr, end=''); print(': ', end=''); print(data_byte_array)
                #data_byte_array = ([3, 4, 5, 6])
                stat = rfid.nTAG2xxWrite(page_adr, data_byte_array)
                tag_write_success = False
                if stat == rfid.OK:
                    tag_write_success = True
                #tag_write_success = rfid.writeTagData(data, register, tag_chip)
                page_adr = page_adr + 1
                sleep_ms(100)
            #if tag_write_success is True:
            page_adr = page_adr_min
            total_string = ''
            while page_adr <= page_adr_max:
                raw_data = rfid.read(page_adr)
                page_text = "".join(chr(x) for x in raw_data)
                print("ID: ", end=''); print(tag_id)
                print('Text in pages ', end=''); print(page_adr, end=''); print('-', end=''); print(page_adr+3, end=''); print(': ', end=''); print(page_text)
                total_string = total_string + page_text
                print()
                page_adr = page_adr + bytes_per_page
            print('Text on tag: ', end=''); print(total_string)
            break
    sleep_ms(10)
