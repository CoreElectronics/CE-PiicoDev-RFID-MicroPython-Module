# PiicoDev® VEML6030 MicroPython Module

This is the firmware repo for the [Core Electronics PiicoDev® Ambient Light Sensor VEML6030](https://core-electronics.com.au/piicodev-ambient-light-sensor-veml6030.html).

This module depends on the [PiicoDev Unified Library](https://github.com/CoreElectronics/CE-PiicoDev-Unified).

See the Quickstart Guides for:
- [Micro:bit v2](https://core-electronics.com.au/tutorials/piicodev-ambient-light-sensor-veml6030-quickstart-guide-for-micro-bit.html)
- [Raspberry Pi Pico](https://core-electronics.com.au/tutorials/piicodev-ambient-light-sensor-veml6030-quickstart-guide-for-rpi-pico).
- [Raspberry Pi](https://core-electronics.com.au/tutorials/piicodev-raspberrypi/piicodev-ambient-light-sensor-veml6030-raspberry-pi-guide.html)

# Usage
## Example
[main.py](https://github.com/CoreElectronics/CE-PiicoDev-VEML6030-MicroPython-Module/blob/main/main.py) is a simple example to get started.
```
from PiicoDev_VEML6030 import PiicoDev_VEML6030
from time import sleep

# Initialise Sensor
light = PiicoDev_VEML6030()

while True:
    # Read and print light data
    lightVal = light.read()
    print(str(lightVal) + " lux")

    sleep(1)
```
## Details
### PiicoDev_VEML6030(bus=, freq=, sda=, scl=, addr=0x10)
Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
bus | int | 0,1 | Raspberry Pi Pico: 0, Raspberry Pi: 1 | I2C Bus.  Ignored on Micro:bit
freq | int | 100-1000000 | Device dependent | I2C Bus frequency (Hz).  Ignored on Raspberry Pi
sda | Pin | Device Dependent | Device Dependent | I2C SDA Pin. Implemented on Raspberry Pi Pico only
scl | Pin | Device Dependent | Device Dependent | I2C SCL Pin. Implemented on Raspberry Pi Pico only
addr | int | 0x10, 0x48 | 0x10 | This address needs to match the PiicoDev Ambient Light Sensor VEML6030 hardware address configured by the jumper

### PiicoDev_VEML6030.read()
Parameter | Type | Unit | Description
--- | --- | --- | ---
returned | float | lux | Ambient light

### PiicoDev_VEML6030.setGain(gain)
Parameter | Type | Range | Description
--- | --- | --- | ---
gain | float/int | 0.125, 0.5, 1, 2 | Set the gain of the device. Affects resolution and maximum possible illumination. See the [appnote](https://www.vishay.com/docs/84367/designingveml6030.pdf)

# License
This project is open source - please review the LICENSE.md file for further licensing information.

If you have any technical questions, or concerns about licensing, please contact technical support on the [Core Electronics forums](https://forum.core-electronics.com.au/).

*\"PiicoDev\" and the PiicoDev logo are trademarks of Core Electronics Pty Ltd.*
