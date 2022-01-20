from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

print("Place tag near the PiicoDev RFID Module")

while True:
    detect_tag_result = rfid.detectTag()
    tag_present = detect_tag_result['present']
    tag_type = detect_tag_result['type']
    
    if tag_present:
        print(rfid.SelectTagSN())
        print("Tag detected")
        #print(rfid.readID())
        read_tag_id_result = rfid.readTagID()
        tag_success = read_tag_id_result['success']
        tag_id_raw = read_tag_id_result['id']
        tag_id = tag_id_raw[3] + 0xFF*tag_id_raw[2] + 0xFFFF*tag_id_raw[1] + 0xFFFFFF*tag_id_raw[0]
        print(type(tag_id_raw[0]))
        print(hex(tag_id_raw[4]), hex(tag_id_raw[3]), hex(tag_id_raw[2]), hex(tag_id_raw[1]), hex(tag_id_raw[0]))
        print(type(tag_id))
        print(tag_id)
        
        if tag_success:
            print(" - Type: 0x%02x" % tag_type)
            print(" - ID:   0x%02x%02x%02x%02x" % (tag_id_raw[0], tag_id_raw[1], tag_id_raw[2], tag_id_raw[3]))
            print("")
            if rfid.select_tag(tag_id_raw) == rfid.OK:
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            else:
                print("Failed to select tag")
            sleep_ms(1000)
    sleep_ms(10)
    
