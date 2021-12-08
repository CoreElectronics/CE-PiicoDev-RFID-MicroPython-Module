# PiicoDev MFRC522 minimal example code

from PiicoDev_MFRC522 import *
# Initialise Sensor
scanner = PiicoDev_MFRC522()


    # Read and print light data

print("")
print("Place card before reader to read from address 0x08")
print("")

#try:
while True:

    (stat, tag_type) = scanner.request(scanner.REQIDL)
    print(stat)
    print(tag_type)
    if stat == scanner.OK:

        (stat, raw_uid) = scanner.anticoll()
        
        if stat == scanner.OK:
            print("New card detected")
            print("  - tag type: 0x%02x" % tag_type)
            print("  - uid  : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
            print("")

            if scanner.select_tag(raw_uid) == scanner.OK:

                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                if scanner.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
                    print("Address 8 data: %s" % rdr.read(8))
                    scanner.stop_crypto1()
                else:
                    print("Authentication error")
            else:
                print("Failed to select tag")
    sleep_ms(1000)

#except KeyboardInterrupt:
#    print("Bye")