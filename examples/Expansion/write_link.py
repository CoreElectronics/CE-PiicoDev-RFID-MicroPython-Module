from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

uri = 'https://www.core-electronics.com.au'

while True:
    if rfid.tagPresent():
        #success = rfid.writeLink(uri)
        #success = rfid.writeURL(url, protocol='http')
        success = rfid.writeLink('mailto:support@core-electronics.com.au')
        if success:
            print('Write successful')
            break
    sleep_ms(10)
