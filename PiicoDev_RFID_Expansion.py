_CMD_TRANCEIVE = 0x0C

# NTAG
_NTAG_NO_BYTES_PER_PAGE = 4
_NTAG_PAGE_ADR_MIN = 4 # user memory is 4 to 39 for NTAG213 so that allows for 144 characters.  So that's 36 pages
_NTAG_PAGE_ADR_MAX = 39

# Classic
_CLASSIC_NO_BYTES_PER_REG = 16
_CLASSIC_ADR = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42, 44, 45, 46, 48]


# ----------------------------- Write -------------------------------------------------

def classicWrite(self, addr, data):
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

# ----------------------------- Write Number --------------------------------------------

def writeNumberToNtag(self, bytes_number, slot=0):
    tag_write_success = False
    assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
    page_adr_min = 4
    stat = self.writePageNtag(page_adr_min+slot, bytes_number)
    tag_write_success = False
    if stat == self.OK:
        tag_write_success = True
    return tag_write_success

def writeNumberToClassic(self, bytes_number, slot=0):
    assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
    while len(bytes_number) < _CLASSIC_NO_BYTES_PER_REG:
        bytes_number.append(0)
    tag_write_success = self.writeClassicRegister(_CLASSIC_ADR[slot], bytes_number)
    return tag_write_success

def writeNumber(self, number, slot=35):
    success = False
    bytearray_number = bytearray(struct.pack('l', number))
    read_tag_id_result = self.readTagID()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
    if read_tag_id_result['success']:
        if read_tag_id_result['type'] == 'ntag':
            success = self.writeNumberToNtag(bytearray_number, slot)
            while success is False:
                success = self.writeNumberToNtag(bytearray_number, slot)
        if read_tag_id_result['type'] == 'classic':
            success = self.writeNumberToClassic(bytearray_number, slot)
            while success is False:
                success = self.writeNumberToClassic(bytearray_number, slot)
    return success

# ----------------------------- Read Number --------------------------------------------

def readNumber(self, slot=35):
    bytearray_number = None
    read_tag_id_result = self.readTagID()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
    if read_tag_id_result['type'] == 'ntag':
        page_address = 4
        bytearray_number = self.read(page_address+slot)

    if read_tag_id_result['type'] == 'classic':
        bytearray_number = self.readClassicData(_CLASSIC_ADR[slot])
    
    try:
        number = struct.unpack('l', bytes(bytearray_number))
        number = number[0]
        return number
    except:
        print('Error reading card')
        return 0

# ----------------------------- Write Text --------------------------------------------

def writeTextToNtag(self, text, ignore_null=False): # NTAG213
    buffer_start = 0
    for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX):
        data_chunk = text[buffer_start:buffer_start+_NTAG_NO_BYTES_PER_PAGE]
        buffer_start = buffer_start + _NTAG_NO_BYTES_PER_PAGE
        data_byte_array = [ord(x) for x in list(data_chunk)]
        while len(data_byte_array) < _NTAG_NO_BYTES_PER_PAGE:
            data_byte_array.append(0)
        tag_write_success = self.writePageNtag(page_adr, data_byte_array)
        if ignore_null is False:
            if 0 in data_byte_array: # Null found.  Job complete.
                return tag_write_success
    return tag_write_success

def writeTextToClassic(self, text, ignore_null=False):
    buffer_start = 0
    x = 0
    for slot in range(9):
        data_chunk = text[buffer_start:buffer_start+_CLASSIC_NO_BYTES_PER_REG]
        buffer_start = buffer_start + _CLASSIC_NO_BYTES_PER_REG
        data_byte_array = [ord(x) for x in list(data_chunk)]
        while len(data_byte_array) < _CLASSIC_NO_BYTES_PER_REG:
            data_byte_array.append(0)
        tag_write_success = self.writeClassicRegister(_CLASSIC_ADR[slot], data_byte_array)
        if ignore_null is False:
            if 0 in data_byte_array: # Null found.  Job complete.
                return tag_write_success
    return tag_write_success

def writeText(self, text, ignore_null=False):
    success = False
    maximum_characters = 144
    text = text + '\0'
    read_tag_id_result = self.readTagID()
    if read_tag_id_result['type'] == 'ntag':
        success = self.writeTextToNtag(text, ignore_null=ignore_null)
    if read_tag_id_result['type'] == 'classic':
        success = self.writeTextToClassic(text, ignore_null=ignore_null)
    return success

# ----------------------------- Read Text --------------------------------------------

def readTextFromNtag(self):
    page_adr = _NTAG_PAGE_ADR_MIN
    total_string = ''
    while page_adr <= _NTAG_PAGE_ADR_MAX:
        raw_data = self.read(page_adr)
        print(raw_data)
        page_text = "".join(chr(x) for x in raw_data)
        total_string = total_string + page_text
        if 0 in raw_data: # Null found.  Job complete.
            substring = total_string.split('\0')
            return substring[0]
        page_adr = page_adr + _NTAG_NO_BYTES_PER_PAGE
    return total_string

def readTextFromClassic(self):
    x = 0
    total_string = ''
    for slot in range(9):
        reg_data = self.readClassicData(_CLASSIC_ADR[slot])
        reg_text = "".join(chr(x) for x in reg_data)
        total_string = total_string + reg_text
        print(reg_data)
        if 0 in reg_data: # Null found.  Job complete.
            substring = total_string.split('\0')
            return substring[0]
    return total_string

def readText(self):
    text = ''
    read_tag_id_result = self.readTagID()
    while read_tag_id_result['success'] is False:
        read_tag_id_result = self.readTagID()
    if read_tag_id_result['type'] == 'ntag':
        text = self.readTextFromNtag()
    if read_tag_id_result['type'] == 'classic':
        text = self.readTextFromClassic()
    return text

# ----------------------------- Write Link --------------------------------------------

def writeLink(self, uri): # Currently only supported by NTAG213
    is_ndef_message = chr(3)
    ndef_length = chr(len(uri) + 5)
    ndef_record_header = chr(209)
    ndef_type_length = chr(1)
    ndef_payload_length = chr(len(uri) + 1)
    is_uri_record = chr(85)
    record_type_indicator = chr(0)
    tlv_terminator = chr(254)
    ndef = is_ndef_message + ndef_length + ndef_record_header + ndef_type_length + ndef_payload_length + is_uri_record + record_type_indicator + uri + tlv_terminator
    print(ndef)
    success = self.writeText(ndef, ignore_null=True)
    return success
