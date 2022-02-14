# https://github.com/semaf/MFRC522_I2C_Library/blob/master/src/MFRC522_I2C.cpp
# https://github.com/wendlers/micropython-mfrc522/blob/master/mfrc522.py
# https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf
# https://stackoverflow.com/questions/36915264/writing-ntag213-mifare-ultralight-c-with-mxgxw-mfrc522-python-library-and-mfrc
# https://github.com/mxgxw/MFRC522-python
# https://stackoverflow.com/questions/4286447/how-to-calculate-the-crc-in-rfid-protocol

from PiicoDev_Unified import *
import struct

compat_str = '\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'

_SYSNAME = os.uname().sysname

_I2C_ADDRESS        = 0x2C

_REG_COMMAND        = 0x01
_REG_COM_I_EN       = 0x02
_REG_DIV_I_EN       = 0x03
_REG_COM_IRQ        = 0x04
_REG_DIV_IRQ        = 0x05
_REG_ERROR          = 0x06
_REG_STATUS_1       = 0x07
_REG_STATUS_2       = 0x08
_REG_FIFO_DATA      = 0x09
_REG_FIFO_LEVEL     = 0x0A
_REG_CONTROL        = 0x0C
_REG_BIT_FRAMING    = 0x0D
_REG_MODE           = 0x11
_REG_TX_CONTROL     = 0x14
_REG_TX_ASK         = 0x15
_REG_CRC_RESULT_MSB = 0x21
_REG_CRC_RESULT_LSB = 0x22
_REG_T_MODE         = 0x2A
_REG_T_PRESCALER    = 0x2B
_REG_T_RELOAD_HI    = 0x2C
_REG_T_RELOAD_LO    = 0x2D
_REG_AUTO_TEST      = 0x36
_REG_VERSION        = 0x37
_CMD_IDLE           = 0x00
_CMD_CALC_CRC       = 0x03
_CMD_TRANCEIVE      = 0x0C
_CMD_MF_AUTHENT     = 0x0E
_CMD_SOFT_RESET     = 0x0F

# RFID Tag (Proximity Integrated Circuit Card)
_TAG_CMD_REQIDL  = 0x26
_TAG_CMD_REQALL  = 0x52
_TAG_CMD_ANTCOL1 = 0x93
_TAG_CMD_ANTCOL2 = 0x95
_TAG_CMD_ANTCOL3 = 0x97

# Classic
_TAG_AUTH_KEY_A = 0x60
_CLASSIC_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# PiicoDev Merge NTAG & Classic
_SLOT_NO_MIN = 0
_SLOT_NO_MAX = 35

def _readBit(x, n):
    return x & 1 << n != 0

def _setBit(x, n):
    return x | (1 << n)

def _clearBit(x, n):
    return x & ~(1 << n)

def _writeBit(x, n, b):
    if b == 0:
        return _clearBit(x, n)
    else:
        return _setBit(x, n)

def _writeCrumb(x, n, c):
    x = _writeBit(x, n, _readBit(c, 0))
    return _writeBit(x, n+1, _readBit(c, 1))

class PiicoDev_RFID(object):
    OK = 1
    NOTAGERR = 2
    ERR = 3

    def __init__(self, bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, suppress_warnings=False):
        try:
            if compat_ind >= 1:
                pass
            else:
                print(compat_str)
        except:
            print(compat_str)
        self.i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        self.address = address
        self._tag_present = False
        self._read_tag_id_success = False
        self.reset()
        sleep_ms(50)
        self._wreg(_REG_T_MODE, 0x80)
        self._wreg(_REG_T_PRESCALER, 0xA9)
        self._wreg(_REG_T_RELOAD_HI, 0x03)
        self._wreg(_REG_T_RELOAD_LO, 0xE8)
        self._wreg(_REG_TX_ASK, 0x40)
        self._wreg(_REG_MODE, 0x3D)
        self._wreg(_REG_DIV_I_EN, 0x80) # CMOS Logic for IRQ pin
        self._wreg(_REG_COM_I_EN, 0x20) # allows the receiver interrupt request (RxIRq bit) to be propagated to pin IRQ
        self.antenna_on()
        if _SYSNAME is 'microbit' and not suppress_warnings:
            print('This library can only be used to get tag IDs.\nAdvanced methods such as reading and wring to tag memory are not available on Micro:bit due to the limited storage available.\nTo run advanced methods, use a Raspberry Pi Pico instead of Micro:bit.\nTo suppress this warning, initialise with PiicoDev_RFID(suppress_warnings=True)\n')

    def _wreg(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    def _wfifo(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes(val))

    def _rreg(self, reg):
        val = self.i2c.readfrom_mem(self.address, reg, 1)
        return val[0]
    
    def _sflags(self, reg, mask):
        current_value = self._rreg(reg)
        self._wreg(reg, current_value | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        if cmd == _CMD_MF_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == _CMD_TRANCEIVE:
            irq_en = 0x77
            wait_irq = 0x30
        self._wreg(_REG_COMMAND, _CMD_IDLE) # Stop any active command.
        self._wreg(_REG_COM_IRQ, 0x7F)      # Clear all seven interrupt request bits
        self._sflags(_REG_FIFO_LEVEL, 0x80) # FlushBuffer = 1, FIFO initialization
        self._wfifo(_REG_FIFO_DATA, send)   # Write to the FIFO
        if cmd == _CMD_TRANCEIVE:
            self._sflags(_REG_BIT_FRAMING, 0x00) # This starts the transceive operation
        self._wreg(_REG_COMMAND, cmd)
        if cmd == _CMD_TRANCEIVE:
            self._sflags(_REG_BIT_FRAMING, 0x80) # This starts the transceive operation

        i = 20000  #2000
        while True:
            n = self._rreg(_REG_COM_IRQ)
            i -= 1
            if n & wait_irq:
                break
            if n & 0x01:
                break
            if i == 0:
                break
        self._cflags(_REG_BIT_FRAMING, 0x80)
        
        if i:
            if (self._rreg(_REG_ERROR) & 0x1B) == 0x00:
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == _CMD_TRANCEIVE:
                    n = self._rreg(_REG_FIFO_LEVEL)
                    lbits = self._rreg(_REG_CONTROL) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(_REG_FIFO_DATA))
            else:
                stat = self.ERR
        return stat, recv, bits

    def _crc(self, data):
        self._wreg(_REG_COMMAND, _CMD_IDLE)
        self._cflags(_REG_DIV_IRQ, 0x04)
        self._sflags(_REG_FIFO_LEVEL, 0x80)

        for c in data:
            self._wreg(_REG_FIFO_DATA, c)
        self._wreg(_REG_COMMAND, _CMD_CALC_CRC)

        i = 0xFF
        while True:
            n = self._rreg(_REG_DIV_IRQ)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        self._wreg(_REG_COMMAND, _CMD_IDLE)
        return [self._rreg(_REG_CRC_RESULT_LSB), self._rreg(_REG_CRC_RESULT_MSB)]

    def reset(self):
        self._wreg(_REG_COMMAND, _CMD_SOFT_RESET)

    def antenna_on(self, on=True):
        if on and ~(self._rreg(_REG_TX_CONTROL) & 0x03):
            self._sflags(_REG_TX_CONTROL, 0x83)
        else:
            self._cflags(_REG_TX_CONTROL, b'\x03')
              
    def request(self, mode):
        self._wreg(_REG_BIT_FRAMING, 0x07)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, [mode])
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR

        return stat, bits

    def anticoll(self, anticolN=_TAG_CMD_ANTCOL1):
        ser_chk = 0
        ser = [anticolN, 0x20]

        self._wreg(_REG_BIT_FRAMING, 0x00)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, ser)
        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR
        return stat, recv

    def select_tag(self, ser):
        buf = [0x93, 0x70] + ser[:5]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

    def auth(self, mode, addr, sect, ser):
        return self._tocard(_CMD_MF_AUTHENT, [mode, addr] + sect + ser[:4])[0]

    def stop_crypto1(self):
        self._cflags(_REG_STATUS_2, 0x08)

    def read(self, addr):
        data = [0x30, addr]
        data += self._crc(data)
        (stat, recv, _) = self._tocard(_CMD_TRANCEIVE, data)
        return recv if stat == self.OK else None

    def writePageNtag(self, page, data):
        buf = [0xA2, page]
        buf += data
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        return stat

    def SelfTest(self): # page 82
        self.reset()
        self._wreg(_REG_FIFO_DATA, bytes([25]))
        self._wreg(_REG_AUTO_TEST, 0x09)
        self._wreg(_REG_FIFO_DATA, 0x00)
        self._wreg(_REG_COMMAND, _CMD_CALC_CRC)
        sleep_ms(1000)
        test_output = self.i2c.readfrom_mem(self.addr, _REG_FIFO_DATA, 64)
        version = self.i2c.readfrom_mem(self.addr, _REG_VERSION, 1)
        
    def readID(self):
        stat, bits = self.request(_TAG_CMD_REQIDL)
        return stat, bits
    
    def SelectTagSN(self):
        valid_uid=[]
        (status,uid)= self.anticoll(_TAG_CMD_ANTCOL1)
        if status != self.OK:
            return  (self.ERR,[])
        
        if self.PcdSelect(uid,_TAG_CMD_ANTCOL1) == 0:
            return (self.ERR,[])
        
        if uid[0] == 0x88 : # NTAG
            valid_uid.extend(uid[1:4])
            (status,uid)=self.anticoll(_TAG_CMD_ANTCOL2)
            if status != self.OK:
                return (self.ERR,[])
            rtn =  self.PcdSelect(uid,_TAG_CMD_ANTCOL2)
            if rtn == 0:
                return (self.ERR,[])
            #now check again if uid[0] is 0x88
            if uid[0] == 0x88 :
                valid_uid.extend(uid[1:4])
                (status , uid) = self.anticoll(_TAG_CMD_ANTCOL3)
                if status != self.OK:
                    return (self.ERR,[])
                if self.MFRC522_PcdSelect(uid,_TAG_CMD_ANTCOL3) == 0:
                    return (self.ERR,[])
        valid_uid.extend(uid[0:5])
        return (self.OK , valid_uid[:len(valid_uid)-1])
    
    def PcdSelect(self, serNum,anticolN):
        backData = []
        buf = []
        buf.append(anticolN)
        buf.append(0x70)
        for i in serNum:
            buf.append(i)
        pOut = self._crc(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self._tocard( 0x0C, buf)
        if (status == self.OK) and (backLen == 0x18):
            return  1
        else:
            return 0
        
    def detectTag(self):
        (stat, ATQA) = self.request(_TAG_CMD_REQIDL)
        _present = False
        if stat is self.OK:
            _present = True
        self._tag_present = _present
        return {'present':_present, 'ATQA':ATQA}

    def _readTagID(self):
        (stat, id) = self.SelectTagSN()
        _success = True
        if stat is self.OK:
            _success = True
        id_formatted = ''
        for i in range(0,len(id)):
            if i > 0:
                id_formatted = id_formatted + ':'
            if id[i] < 16:
                id_formatted = id_formatted + '0'
            id_formatted = id_formatted + hex(id[i])[2:]
        type = 'ntag'
        if len(id) == 4:
            type = 'classic'
        return {'success':_success, 'id_integers':id, 'id_formatted':id_formatted.upper(), 'type':type}
    
    def writeClassicRegister(self, register, data_byte_array):
        while True:
            auth_result = 0
            (stat, tag_type) = self.request(_TAG_CMD_REQIDL)

            if stat == self.OK:
                (stat, raw_uid) = self.anticoll()

                if stat == self.OK:
                    if self.select_tag(raw_uid) == self.OK:
                        auth_result = self.auth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                        if (auth_result == self.OK):
                            stat = self.classicWrite(register, data_byte_array)
                            self.stop_crypto1()
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
    
    def readClassicData(self, register):
        tag_data = None
        auth_result = 0
        while tag_data is None:
            (stat, tag_type) = self.request(_TAG_CMD_REQIDL)
            if stat == self.OK:
                (stat, raw_uid) = self.anticoll()
                if stat == self.OK:
                    if self.select_tag(raw_uid) == self.OK:
                        auth_result = self.auth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                        if (auth_result == self.OK):
                            tag_data = self.read(register)
                            self.stop_crypto1()
                            return tag_data
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")
            sleep_ms(10)

    def readTagID(self):
        detect_tag_result = self.detectTag()
        if detect_tag_result['present'] is False: #Try again, the card may not be in the correct state
            detect_tag_result = self.detectTag()
        if detect_tag_result['present']:
            read_tag_id_result = self._readTagID()
            if read_tag_id_result['success']:
                self._read_tag_id_success = True
                return {'success':read_tag_id_result['success'], 'id_integers':read_tag_id_result['id_integers'], 'id_formatted':read_tag_id_result['id_formatted'], 'type':read_tag_id_result['type']}
        self._read_tag_id_success = False
        return {'success':False, 'id_integers':[0], 'id_formatted':'', 'type':''}

    def readID(self):
        tagId = self.readTagID()
        return tagId['id_formatted']

    def tagPresent(self):
        id = self.readTagID()
        return id['success']
    
    if _SYSNAME != 'microbit':
        try:
            from PiicoDev_RFID_Expansion import classicWrite, writeNumberToNtag, writeNumberToClassic, writeNumber, readNumber, writeTextToNtag, writeTextToClassic, writeText, readTextFromNtag, readTextFromClassic, readText, writeLink 
        except:
            print('Install PiicoDev_RFID_Expansion.py for full functionality')
