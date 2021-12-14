# PiicoDev MFRC522 minimal example code

from PiicoDev_MFRC522 import *
#from mfrc522 import MFRC522
#from PiicoDev_Unified import sleep_ms
# Initialise Sensor
scanner = PiicoDev_MFRC522()
#reader = PiicoDev_MFRC522

    # Read and print light data


print("")
print("Place card before reader to read from address 0x08")
print("")

scanner.init()



def readRFID():
     
    PreviousCard=[0]
    
    print(PreviousCard)
    (stat, tag_type) = scanner.readID()
    #print('stat')
    #print(stat)
    if stat == scanner.OK:
        (stat, uid) = scanner.SelectTagSN()
        if uid == PreviousCard: # if we read the same card twice in a row, ignore it
            return
        if stat == scanner.OK: # we got a valid card!
            idHex = hex(int.from_bytes(bytes(uid),"little",False)).upper() # convert unique ID to a 4-character string for easy account-keeping
            idString = idHex[-4:]
            PreviousCard = uid
            
            #if idString in vehicles.keys(): # have we seen this vehicle before?
            #    vehicles[idString] += 1 # increment its bill by this many dollars
            #else:
            #    vehicles[idString] = 1 # start a fresh bill
                
            print("Vehicle ID: {}   Trip count: ".format(idString))
        else:
            pass
    else:
        PreviousCard=[0]


#try:


def do_write():

    print("")
    print("Place card before reader to write address 0x08")
    print("")

    try:
        while True:

            (stat, tag_type) = scanner.request(scanner.REQIDL)

            if stat == scanner.OK:
                print('scanner is ok')
                (stat, raw_uid) = scanner.anticoll()

                if stat == scanner.OK:
                    print("New card detected")
                    print("  - tag type: 0x%02x" % tag_type)
                    print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    print("")

                    if scanner.select_tag(raw_uid) == scanner.OK:

                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                        if scanner.auth(scanner.AUTHENT1A, 8, key, raw_uid) == scanner.OK:
                            pet_name = 'Sophie          '
                            if len(pet_name) > 16:
                                pet_name = pet_name_byte_array[:16]
                            pet_name_encoded = pet_name.encode()
                            print('Pet Name:')
                            print(pet_name_encoded)
                            #pet_name_byte_array = bytearray(pet_name_encoded)
                            
                            #stat = scanner.write(8, b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0e")
                            
                            pet_name_byte_array = [ord(x) for x in list(pet_name)]
                            print(pet_name_byte_array)
                            stat = scanner.write(8, pet_name_byte_array)
                            scanner.stop_crypto1()
                            if stat == scanner.OK:
                                print("Data written to card")
                            else:
                                print("Failed to write data to card")
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")

    except KeyboardInterrupt:
        print("Bye")        


def do_read():

    print("")
    print("Place card before reader to read from address 0x08")
    print("")

    try:
        while True:

            (stat, tag_type) = scanner.request(scanner.REQIDL)
            
            if stat == scanner.OK:

                (stat, raw_uid) = scanner.anticoll()

                if stat == scanner.OK:
                    print("New card detected")
                    print("  - tag type: 0x%02x" % tag_type)
                    print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    print("")

                    if scanner.select_tag(raw_uid) == scanner.OK:

                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                        if scanner.auth(scanner.AUTHENT1A, 8, key, raw_uid) == scanner.OK:
                            raw_data = scanner.read(8)
                            print("Address 8 data: %s" % raw_data)
                            pet_name_from_tag = "".join(chr(x) for x in raw_data)
                            print(pet_name_from_tag)
                            scanner.stop_crypto1()
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")

    except KeyboardInterrupt:
        print("Bye")

readRFID()
scanner.write(0x08, 8)
while True:
    #readRFID()
    #do_write()
    do_read()
    print(scanner.read(0x08))
    
    sleep_ms(1000)
    
# 
#     (stat, tag_type) = scanner.request(scanner.REQIDL)
#     print(stat)
#     print(tag_type)
#     #scanner.SelfTest()
#     
#     if stat == scanner.OK:
# 
#         (stat, raw_uid) = scanner.anticoll()
#         
#         if stat == scanner.OK:
#             print("New card detected")
#             print("  - tag type: 0x%02x" % tag_type)
#             print("  - uid  : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
#             print("")
# 
#             if scanner.select_tag(raw_uid) == scanner.OK:
# 
#                 key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
# 
#                 if scanner.auth(scanner.AUTHENT1A, 8, key, raw_uid) == scanner.OK:
#                     print("Address 8 data: %s" % scanner.read(8))
#                     scanner.stop_crypto1()
#                 else:
#                     print("Authentication error")
#             else:
#                 print("Failed to select tag")
#     sleep_ms(1000)

#except KeyboardInterrupt:
#    print("Bye")