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
from PiicoDev_RFID import *

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    read_tag_id_result = rfid.readTagID()
    tag_success = read_tag_id_result['success']
    tag_id = read_tag_id_result['id_formatted']

    if tag_success:
        print("ID: ", end=''); print(tag_id)
        sleep_ms(1000)
    sleep_ms(10)
```
## Details
### PiicoDev_RFID(bus=, freq=, sda=, scl=, addr=0x10)
Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
bus | int | 0,1 | Raspberry Pi Pico: 0, Raspberry Pi: 1 | I2C Bus.  Ignored on Micro:bit
freq | int | 100-1000000 | Device dependent | I2C Bus frequency (Hz).  Ignored on Raspberry Pi
sda | Pin | Device Dependent | Device Dependent | I2C SDA Pin. Implemented on Raspberry Pi Pico only
scl | Pin | Device Dependent | Device Dependent | I2C SCL Pin. Implemented on Raspberry Pi Pico only
addr | int | 0x2C, 0x2D, 0x2E, 0x2F | 0x2C | This address needs to match the PiicoDev RFID Module ASW microswitches:<br>[OFF:OFF] 0x2C<br>[ON :OFF] 0x2D<br>[OFF:ON ] 0x2E<br>[ON :ON ] 0x2F

### PiicoDev_RFID.readTagID()
Parameter | Type | Range | Description
--- | --- | --- | ---
Returns | Dictionary |
id_integers | int list | 0-255
id_formatted | str | length 11 or 20
type | str | 'ntag' or 'classic'
success | bool |

### PiicoDev_VEML6030.setGain(gain)
Parameter | Type | Range | Description
--- | --- | --- | ---
gain | float/int | 0.125, 0.5, 1, 2 | Set the gain of the device. Affects resolution and maximum possible illumination. See the [appnote](https://www.vishay.com/docs/84367/designingveml6030.pdf)

# License
This project is open source - please review the LICENSE.md file for further licensing information.

If you have any technical questions, or concerns about licensing, please contact technical support on the [Core Electronics forums](https://forum.core-electronics.com.au/).

*\"PiicoDev\" and the PiicoDev logo are trademarks of Core Electronics Pty Ltd.*
