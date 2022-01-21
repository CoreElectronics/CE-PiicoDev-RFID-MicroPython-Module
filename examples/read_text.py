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
            # [ IN PROGRESS
            tag_id_int = read_tag_id_result['id_integers']
            print(tag_id_int)
            if rfid.select_tag(tag_id_int) == rfid.OK:
                
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                if scanner.auth(rfid.AUTHENT1A, 8, key, tag_id_int) == scanner.OK:
                    raw_data = rfid.read(8)
                    print("Address 8 data: %s" % raw_data)
                    print(type(raw_data))
                    if raw_data is not None:
                        pet_name_from_tag = "".join(chr(x) for x in raw_data)
                        print(pet_name_from_tag)
                    rfid.stop_crypto1()
                else:
                    print("Authentication error")
            else:
                print("Failed to select tag")
            # IN PROGRESS ]
            sleep_ms(1000)
    sleep_ms(10)
