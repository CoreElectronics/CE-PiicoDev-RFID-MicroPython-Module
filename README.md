# PiicoDev® RFID MicroPython Module

This is the firmware repo for the [Core Electronics PiicoDev® RFID Module](https://core-electronics.com.au/piicodev-rfid-module.html).

This module depends on the [PiicoDev Unified Library](https://github.com/CoreElectronics/CE-PiicoDev-Unified).

<!--See the Quickstart Guides for:
- [Micro:bit v2](https://core-electronics.com.au/tutorials/piicodev-ambient-light-sensor-veml6030-quickstart-guide-for-micro-bit.html)
- [Raspberry Pi Pico](https://core-electronics.com.au/tutorials/piicodev-ambient-light-sensor-veml6030-quickstart-guide-for-rpi-pico).
- [Raspberry Pi](https://core-electronics.com.au/tutorials/piicodev-raspberrypi/piicodev-ambient-light-sensor-veml6030-raspberry-pi-guide.html)
-->

# Usage
## Compatibility
This is compatible with NTAG213 and Classic tags.
## Example
[read_id.py](https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/blob/main/examples/read_id.py) is a simple example to get started.
```
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print('')

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readId()   # get the id
        print(id)            # print the id

    sleep_ms(100)
```
## Details
### `PiicoDev_RFID(bus=, freq=, sda=, scl=, addr=0x2C)`
Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
bus | int | 0,1 | Raspberry Pi Pico: 0, Raspberry Pi: 1 | I2C Bus.  Ignored on Micro:bit
freq | int | 100-1000000 | Device dependent | I2C Bus frequency (Hz).  Ignored on Raspberry Pi
sda | Pin | Device Dependent | Device Dependent | I2C SDA Pin. Implemented on Raspberry Pi Pico only
scl | Pin | Device Dependent | Device Dependent | I2C SCL Pin. Implemented on Raspberry Pi Pico only
addr | int | 0x2C, 0x2D, 0x2E, 0x2F | 0x2C | This address needs to match the PiicoDev RFID Module ASW microswitches:<br>[OFF:OFF] 0x2C<br>[ON :OFF] 0x2D<br>[OFF:ON ] 0x2E<br>[ON :ON ] 0x2F

### `PiicoDev_RFID.tagPresent()`
Detects a tag.
Returned Type | Description
--- | ---
bool | True if a tag is detected

### `PiicoDev_RFID.readID()`
Reads the tag ID.
Returned Type | Range | Description
--- | --- | ---
str | 11 or 20 characters | Returns the ID in a format XX:XX:XX:XX:XX:XX:XX for NTAG213 and XX:XX:XX:XX for Classic

### `PiicoDev_RFID.readTagID()`
Returns detailed information about the tag.
Parameter | Type | Range | Description
--- | --- | --- | ---
**Returns** | **Dictionary**
id_integers | int list | 0-255 |7 integers for NTAG213<br>4 integers for Classic tags
id_formatted | str | length 11 or 20 | ID in a format XX:XX:XX:XX:XX:XX:XX for NTAG213 and XX:XX:XX:XX for Classic
type | str | 'ntag' or 'classic' | 
success | bool | | True if the operation is successful

### `PiicoDev_RFID.antennaOn()`
Turn the antenna on.  For normal operation this method does not need to be called.

### `PiicoDev_RFID.antennaOff()`
Turn the antenna off.  For normal operation this method does not need to be called.

### `PiicoDev_RFID.reset()`
Reset the RFID Module.  For normal operation this method does not need to be called.

## Expansion methods
The methods listed below require the `PiicoDev_RFID_Expansion.py` file to be placed in the same directory as `PiicoDev_RFID.py`.  They are only available for Raspberry Pi and Raspberry Pi Pico.  There is not enough program storage to run these methods on a Micro:bit.

### `PiicoDev_RFID.writeNumber(int, slot=35)`
Not available for Micro:bit.  Writes a number to a slot in the tag's memory.  Each slot is mapped to an appropriate location on the tag's memory.
Parameter | Type | Range                          | Default                | Description
---       | ---  | ---                            | -------                | -----------
number    | int  | −2,147,483,647, +2,147,483,647 |       
slot      | int  | 0 - 35                         | 35
**return**|
bool      | bool |                                |                        | True if tag write successful

### `PiicoDev_RFID.readNumber(slot=35)`
Not available for Micro:bit.  Reads a number from a slot in the tag's memory.  Each slot is mapped to an appropriate location on the tag's memory.
Parameter | Type | Range                          | Default                | Description
---       | ---  | ---                            | ---                    | ---
slot      | int  | 0 - 35                         | 35                     | 
**return**|
number    | int  | −2,147,483,647, +2,147,483,647 |                        | Number in slot

### `PiicoDev_RFID.writeText(str)`
Not available for Micro:bit.  Writes text to the tag.
Parameter | Type | Range                          | Default                | Description
---       | ---  | ---                            | -------                | -----------
text      | str  | 1 - 144 Characters |       
**return**|
bool      | bool |                                |                        | True if tag write successful

### `PiicoDev_RFID.readText()`
Not available for Micro:bit.  Reads text from the tag.
Parameter | Type | Range                          | Default                | Description
---       | ---  | ---                            | ---                    | ---
**return**|
text      | str  | 1 - 144 Characters             |                        | Text on the tag

### `PiicoDev_RFID.writeLink(uri)`
__Compatible with NTAG only__.  Not available for Micro:bit.  Writes a URI to the tag.  Most RFID enabled phones will open the link automatically after reading the tag.  This is useful for embedding web or email addresses.  Supports any URI schemes such as `https:`, `http:`, `mailto:` and `tel:`
Parameter | Type | Range                           | Description
---       | ---  | ---                             | ---
uri       | str  | 136 Characters max              | Full URI eg:<br>`https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/edit/main/README.md`
**return**|
success   | bool |                                 | True if tag write successful

# License
This project is open source - please review the LICENSE.md file for further licensing information.

If you have any technical questions, or concerns about licensing, please contact technical support on the [Core Electronics forums](https://forum.core-electronics.com.au/).

*\"PiicoDev\" and the PiicoDev logo are trademarks of Core Electronics Pty Ltd.*
