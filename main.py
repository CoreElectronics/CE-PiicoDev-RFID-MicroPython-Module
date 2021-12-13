# PiicoDev MFRC522 minimal example code

from PiicoDev_MFRC522 import *
#from mfrc522 import MFRC522
#from PiicoDev_Unified import sleep_ms
# Initialise Sensor
scanner = PiicoDev_MFRC522()
#reader = PiicoDev_MFRC522

    # Read and print light data

PreviousCard=[0]

print("")
print("Place card before reader to read from address 0x08")
print("")

scanner.init()



def readRFID():
     
    #global PreviousCard
    
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
readRFID()
scanner.write(0x08, 7)
while True:
    readRFID()
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
#                 if scanner.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
#                     print("Address 8 data: %s" % rdr.read(8))
#                     scanner.stop_crypto1()
#                 else:
#                     print("Authentication error")
#             else:
#                 print("Failed to select tag")
#     sleep_ms(1000)

#except KeyboardInterrupt:
#    print("Bye")