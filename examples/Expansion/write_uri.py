# Demonstrate some different URIs (Unique Resource Identifiers)
# Write a URI to a NTAG - when the tag is scanned a NFC-enabled smartphone the relevant resource will be opened.

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()

print('Hold tag near the PiicoDev RFID Module to write a URI')
print('')

# URIs can link loads of different resources. Here's just a few examples, but there are many more listed here: https://en.wikipedia.org/wiki/List_of_URI_schemes
web_address = 'https://core-electronics.com.au/tutorials/search/query/piicodev/' # URL of a webpage
geo_location = 'geo:-0.6770672,-78.4507881'        # co-ordinates (latitude, longitude) for a map application
email_address = 'mailto:yourusername@example.com'  # compose an email to this recipient
phone = 'tel:##########'                           # call a telephone number (country codes accepted eg. '+61...')

while True:
    if rfid.tagPresent():
        success = rfid.writeURI(web_address) # Write the selected URI to a tag
        if success:
            print('Write successful')
            break # break out of the loop, stopping the script.
    sleep_ms(10)
