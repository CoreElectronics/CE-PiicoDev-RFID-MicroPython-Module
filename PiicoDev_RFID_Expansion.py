# Enables reading and writing of data to tags using the Core Electronics PiicoDev RFID Module
# Ported by Peter Johnston at Core Electronics February 2022
# Original Repos:
# 2021-12-01:
# https://github.com/semaf/MFRC522_I2C_Library
# 2021-12-01:
# https://github.com/wendlers/micropython-mfrc522
# 2021-12-01:
# https://github.com/mxgxw/MFRC522-python

from PiicoDev_Unified import *
import struct
from time import time as now

_REG_STATUS_2   = 0x08
_CMD_TRANCEIVE  = 0x0C
_CMD_MF_AUTHENT = 0x0E


# RFID Tag (Proximity Integrated Circuit Card)
_TAG_CMD_REQIDL  = 0x26

# NTAG
_NTAG_NO_BYTES_PER_PAGE = 4
_NTAG_PAGE_ADR_MIN = 4 # user memory is 4 to 39 for NTAG213 so that allows for 144 characters.  So that's 36 pages
_NTAG_PAGE_ADR_MAX = 39

# Classic
_TAG_AUTH_KEY_A = 0x60
_CLASSIC_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
_CLASSIC_NO_BYTES_PER_REG = 16
_CLASSIC_ADR = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42, 44, 45, 46, 48]

# PiicoDev Merge NTAG & Classic
_SLOT_NO_MIN = 0
_SLOT_NO_MAX = 35

# Required for Classic Tag only - Select a specific tag for reading & writing
def _classicSelectTag(self, ser):
    buf = [0x93, 0x70] + ser[:5]
    buf += self._crc(buf)
    (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
    return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

# Required for Classic Tag only - Authenticate the address in memory
def _classicAuth(self, mode, addr, sect, ser):
    return self._tocard(_CMD_MF_AUTHENT, [mode, addr] + sect + ser[:4])[0]

# Required for Classic Tag only - Turn off crypto
def _classicStopCrypto(self):
    self._cflags(_REG_STATUS_2, 0x08)

# ----------------------------- Write -------------------------------------------------

# Write to an NTAG page
def _writePageNtag(self, page, data):
    buf = [0xA2, page]
    buf += data
    buf += self._crc(buf)
    (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
    return stat

# Write to a Classic register
def _classicWrite(self, addr, data):
    buf = [0xA0, addr]
    buf += self._crc(buf)
    (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
    if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
        stat = self.ERR
    else:
        buf = []
        for i in range(_CLASSIC_NO_BYTES_PER_REG):
            buf.append(data[i])
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
            stat = self.ERR
    return stat

# Prepare a Classic to write to a register
def _writeClassicRegister(self, register, data_byte_array):
    while True:
        auth_result = 0
        (stat, tag_type) = self._request(_TAG_CMD_REQIDL)

        if stat == self.OK:
            (stat, raw_uid) = self._anticoll()

            if stat == self.OK:
                if self._classicSelectTag(raw_uid) == self.OK:
                    auth_result = self._classicAuth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                    if (auth_result == self.OK):
                        stat = self._classicWrite(register, data_byte_array)
                        self._classicStopCrypto()
                        if stat == self.OK:
                            return True
                        else:
                            print("Failed to write data to tag")
                            return False
                    else:
                        print("Authentication error")
                        return False
                else:
                    print("Failed to select tag")
                    return False   

# ------------------------------ Read ----------------------------------------------------

# Read a register from NTAG or Classic
def _read(self, addr):
    data = [0x30, addr]
    data += self._crc(data)
    (stat, recv, _) = self._tocard(_CMD_TRANCEIVE, data)
    return recv if stat == self.OK else None

# Prepare a classic to read a register
def _readClassicData(self, register):
    tag_data = None
    auth_result = 0
    while tag_data is None:
        (stat, tag_type) = self._request(_TAG_CMD_REQIDL)
        if stat == self.OK:
            (stat, raw_uid) = self._anticoll()
            if stat == self.OK:
                if self._classicSelectTag(raw_uid) == self.OK:
                    auth_result = self._classicAuth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                    if (auth_result == self.OK):
                        tag_data = self._read(register)
                        self._classicStopCrypto()
                        return tag_data
                    else:
                        print("Authentication error")
                else:
                    print("Failed to select tag")
        sleep_ms(10)

# ----------------------------- Write Number --------------------------------------------

# Writes a number to NTAG
def _writeNumberToNtag(self, bytes_number, slot=0):
    tag_write_success = False
    assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
    page_adr_min = 4
    stat = self._writePageNtag(page_adr_min+slot, bytes_number)
    tag_write_success = False
    if stat == self.OK:
        tag_write_success = True
    return tag_write_success

# Writes a number to Classic
def _writeNumberToClassic(self, bytes_number, slot=0):
    assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
    while len(bytes_number) < _CLASSIC_NO_BYTES_PER_REG:
        bytes_number.append(0)
    tag_write_success = self._writeClassicRegister(_CLASSIC_ADR[slot], bytes_number)
    return tag_write_success

# Writes a number to the tag
def writeNumber(self, number, slot=35):
    success = False
    bytearray_number = bytearray(struct.pack('l', number))
    read_tag_id_result = self.readTagID()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
    if read_tag_id_result['success']:
        if read_tag_id_result['type'] == 'ntag':
            success = self._writeNumberToNtag(bytearray_number, slot)
            while success is False:
                success = self._writeNumberToNtag(bytearray_number, slot)
        if read_tag_id_result['type'] == 'classic':
            success = self._writeNumberToClassic(bytearray_number, slot)
            while success is False:
                success = self._writeNumberToClassic(bytearray_number, slot)
    return success

# ----------------------------- Read Number --------------------------------------------

# Reads a number from the tag
def readNumber(self, slot=35):
    bytearray_number = None
    read_tag_id_result = self.readTagID()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
    if read_tag_id_result['type'] == 'ntag':
        page_address = 4
        bytearray_number = self._read(page_address+slot)

    if read_tag_id_result['type'] == 'classic':
        bytearray_number = self._readClassicData(_CLASSIC_ADR[slot])
    
    try:
        number = struct.unpack('l', bytes(bytearray_number[:4]))
        number = number[0]
        return number
    except:
        print('Error reading card')
        return 0

# ----------------------------- Write Text --------------------------------------------

# Writes text to NTAG.
def _writeTextToNtag(self, text, ignore_null=False): # NTAG213
    buffer_start = 0
    for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX+1):
        data_chunk = text[buffer_start:buffer_start+_NTAG_NO_BYTES_PER_PAGE]
        buffer_start = buffer_start + _NTAG_NO_BYTES_PER_PAGE
        data_byte_array = [ord(x) for x in list(data_chunk)]
        while len(data_byte_array) < _NTAG_NO_BYTES_PER_PAGE:
            data_byte_array.append(0)
        tag_write_success = self._writePageNtag(page_adr, data_byte_array)
        if ignore_null is False:
            if 0 in data_byte_array: # Null found.  Job complete.
                return tag_write_success
    return tag_write_success

# Writes text to Classic.
def _writeTextToClassic(self, text, ignore_null=False):
    buffer_start = 0
    x = 0
    for slot in range(9):
        data_chunk = text[buffer_start:buffer_start+_CLASSIC_NO_BYTES_PER_REG]
        buffer_start = buffer_start + _CLASSIC_NO_BYTES_PER_REG
        data_byte_array = [ord(x) for x in list(data_chunk)]
        while len(data_byte_array) < _CLASSIC_NO_BYTES_PER_REG:
            data_byte_array.append(0)
        tag_write_success = self._writeClassicRegister(_CLASSIC_ADR[slot], data_byte_array)
        if ignore_null is False:
            if 0 in data_byte_array: # Null found.  Job complete.
                return tag_write_success
    return tag_write_success

# Writes text to the tag.
def writeText(self, text, ignore_null=False):
    success = False
    maximum_characters = 144
    text = text + '\0'
    read_tag_id_result = self.readTagID()
    if read_tag_id_result['type'] == 'ntag':
        success = self._writeTextToNtag(text, ignore_null=ignore_null)
    if read_tag_id_result['type'] == 'classic':
        success = self._writeTextToClassic(text, ignore_null=ignore_null)
    return success

# ----------------------------- Read Text --------------------------------------------

# Reads text from NTAG.
def _readTextFromNtag(self):
    total_string = ''
    try:
        for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX+1):
            page_data = self._read(page_adr)[:4]
            page_text = "".join(chr(x) for x in page_data)
            total_string = total_string + page_text
            if 0 in page_data: # Null found.  Job complete.
                substring = total_string.split('\0')
                return substring[0]
            page_adr = page_adr + _NTAG_NO_BYTES_PER_PAGE
    except:
        pass
    return total_string

# Reads text from Classic.
def _readTextFromClassic(self):
    x = 0
    total_string = ''
    try:
        for slot in range(9):
            reg_data = self._readClassicData(_CLASSIC_ADR[slot])
            reg_text = "".join(chr(x) for x in reg_data)
            total_string = total_string + reg_text
            if 0 in reg_data: # Null found.  Job complete.
                substring = total_string.split('\0')
                return substring[0]
    except: pass
    return total_string

# Reads text from the tag.
def readText(self, timeout=0):
    text = ''
    read_tag_id_result = self.readTagID()
    start = now()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
        if timeout > 0 and now() - start > timeout: break # trigger a timeout
    if read_tag_id_result['type'] == 'ntag':
        text = self._readTextFromNtag()
    if read_tag_id_result['type'] == 'classic':
        text = self._readTextFromClassic()
    return text

# ----------------------------- Write Link --------------------------------------------

# Writes a URI to the tag
def writeURI(self, uri): # Currently only supported by NTAG213
    is_ndef_message = chr(3)
    ndef_length = chr(len(uri) + 5)
    ndef_record_header = chr(209)
    ndef_type_length = chr(1)
    ndef_payload_length = chr(len(uri) + 1)
    is_uri_record = chr(85)
    record_type_indicator = chr(0)
    tlv_terminator = chr(254)
    ndef = is_ndef_message + ndef_length + ndef_record_header + ndef_type_length + ndef_payload_length + is_uri_record + record_type_indicator + uri + tlv_terminator
    success = self.writeText(ndef, ignore_null=True)
    return success
