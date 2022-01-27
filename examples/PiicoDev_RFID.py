# https://github.com/semaf/MFRC522_I2C_Library/blob/master/src/MFRC522_I2C.cpp
# https://github.com/wendlers/micropython-mfrc522/blob/master/mfrc522.py
# https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf
# https://stackoverflow.com/questions/36915264/writing-ntag213-mifare-ultralight-c-with-mxgxw-mfrc522-python-library-and-mfrc
# https://github.com/mxgxw/MFRC522-python
# https://stackoverflow.com/questions/4286447/how-to-calculate-the-crc-in-rfid-protocol

from PiicoDev_Unified import *

compat_str = '\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'

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

def rfid_get_crc(data, size):
    lsb = False
    rxdt = False
    crc = 0
    bits = 0
    byte = 0
    i = 0
    RFID_CRC_INIT = 0x3791

    crc = RFID_CRC_INIT;
    for i in range(size):
        bits = 8;
        byte = data[i]; # Next byte
        while (bits > 0):
            bits = bits - 1
            lsb = crc & 1 # Store LSB
            crc >> 1  # Shift right 1 bit
            rxdt = byte & 1
            if (rxdt):
                crc |= 0x8000; # Shift in next bit
            if (lsb): # Check stored LSB
                crc ^= 0x8000 # Invert MSB
            if (0x8000 == (crc & 0x8000)): # Check MSB
                crc ^= 0x0408 # Invert bits 3 and 10
            byte >>= 1 # Next bit
    return crc


class PiicoDev_RFID(object):
    DEBUG = True
    OK = 10   # Can put any number here - not used for communicating past this program
    NOTAGERR = 31  # Can put any number here - not used for communicating past this program
    ERR = 42 # Can put any number here - not used for communicating past this program
   
    AUTHENT1A = 0x60  #0110 0000
    AUTHENT1B = 0x61  #0110 0001
    


    def __init__(self, bus=None, freq=None, sda=None, scl=None, addr=_I2C_ADDRESS):
        try:
            if compat_ind >= 1:
                pass
            else:
                print(compat_str)
        except:
            print(compat_str)
        self.i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        self.addr = addr

        self.init()

    def _wreg(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))
        #self.i2c.writeto_mem(self.addr, reg, bytes(val))
        #self.i2c.write8(self.addr, bytes(reg), bytes(val))

    def _rreg(self, reg):
        val = self.i2c.readfrom_mem(self.addr, reg, 1)
        return val[0]
    
    def _sflags(self, reg, mask):
        current_value = self._rreg(reg)
        self._wreg(reg, current_value | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):
        #print('_tocard cmd')
        #print(cmd)
        #if cmd is 12:
        #    print('_tocard cmd is transcive')
        #print('_tocard send')
        #print(send)
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        if cmd == _CMD_MF_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == _CMD_TRANCEIVE:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(_REG_COM_I_EN, irq_en | 0x80)  # 0x80
        self._cflags(_REG_COM_IRQ, 0x80)
        self._sflags(_REG_FIFO_LEVEL, 0x80)
        self._wreg(_REG_COMMAND, 0x00)

        for c in send:
            self._wreg(_REG_FIFO_DATA, c)
        self._wreg(_REG_COMMAND, cmd)

        if cmd == _CMD_TRANCEIVE:
            self._sflags(_REG_BIT_FRAMING, 0x80) # This starts the transceive operation

        i = 2000
        while True:
            #print('.')
            n = self._rreg(_REG_COM_IRQ)
            i -= 1
            #print('_tocard i')
            #print(i)
            #print('_tocard ~(n & 0x01)')
            #print(~(n & 0x01))
            #print('_tocard ~(n & wait_irq)')
            #print(~(n & wait_irq))
            #print('n')
            #print(n)
            if n & wait_irq:
                #print('_tocard wait irq break')
                break
            if n & 0x01:
                #print('_tocard nothing received in 25ms')
                break
            if i == 0:
                #print('_tocard communication might be down')
                break
        #print('_tocard continue')
        self._cflags(_REG_BIT_FRAMING, 0x80)
        
        if i:
            #print('i is > 0')
            #print(self._rreg(_REG_ERROR))
            if (self._rreg(_REG_ERROR) & 0x1B) == 0x00:
                #print('ok')
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == _CMD_TRANCEIVE:
                    n = self._rreg(_REG_FIFO_LEVEL)
                    #print('_tocard FIFO level')
                    #print(n)
                    lbits = self._rreg(_REG_CONTROL) & 0x07
                    #print('_tocard L Bits')
                    #print(lbits)
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
                    #print('bits')
                    #print(bits)
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(_REG_FIFO_DATA))
            else:
                stat = self.ERR
        #print('stat')
        #print(stat)
        #print('recv')
        #print(recv)
        #print('bits')
        #print(bits)
        return stat, recv, bits

    def _crc(self, data):
        self._wreg(_REG_COMMAND, _CMD_IDLE)
        self._cflags(_REG_DIV_IRQ, 0x04)
        self._sflags(_REG_FIFO_LEVEL, 0x80)
        
        #data.append
        #print('CRC Data')
        #print(data)
        
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

    def init(self):
        #self.reset()
        sleep_ms(50) #not sure if we need this
        #self._wreg(_REG_T_MODE, b'\x80')            #0x80
        self._wreg(_REG_T_MODE, 0x8D)            #0x80
        #self._wreg(_REG_T_PRESCALER, b'\xA9')       #0xA9
        self._wreg(_REG_T_PRESCALER, 0x3E)       #0xA9
        #self._wreg(_REG_T_RELOAD_HI, b'\x03')       #0x03
        self._wreg(_REG_T_RELOAD_HI, 0)       #0x03
        #self._wreg(_REG_T_RELOAD_LO, b'\xE8')       #0xE8
        self._wreg(_REG_T_RELOAD_LO, 30)       #0xE8
        #self._wreg(_REG_TX_ASK, b'\x40')
        self._wreg(_REG_TX_ASK, 0x40)
        #self._wreg(_REG_MODE, b'\x3D')
        self._wreg(_REG_MODE, 0x3D)
        self._wreg(_REG_DIV_I_EN, 0x80)
        self.antenna_on()
        #print('Device Initialised')

    def reset(self):
        self._wreg(_REG_COMMAND, _CMD_SOFT_RESET)

    def antenna_on(self, on=True):
        if on and ~(self._rreg(_REG_TX_CONTROL) & 0x03):
            #print('antenna code here 1')
            
            self._sflags(_REG_TX_CONTROL, 0x83)
            #self._wreg(_REG_TX_CONTROL, 0x03)
        else:
            #print('antenna code here 2')
            self._cflags(_REG_TX_CONTROL, b'\x03')
        #print('antenna status')
        #print(_REG_TX_CONTROL)
        #print(self._rreg(_REG_TX_CONTROL))
              
    def request(self, mode):
        #print('Request Made')
        self._wreg(_REG_BIT_FRAMING, 0x07)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, [mode])
        #print(stat)
        #print(recv)
        #print(bits)
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR

        return stat, bits

    def anticoll(self, anticolN=_TAG_CMD_ANTCOL1):

        ser_chk = 0
        ser = [anticolN, 0x20]

        self._wreg(_REG_BIT_FRAMING, 0x00)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, ser)
        #print(recv, bits)
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
        #print('crypto off')

    def read(self, addr):
        print('reading card')
        print(addr)
        data = [0x30, addr]
        data += self._crc(data)
        print(data)
        (stat, recv, _) = self._tocard(_CMD_TRANCEIVE, data)
        print(stat)
        print(recv)
        return recv if stat == self.OK else None

    def write(self, addr, data, tag_chip):
        if tag_chip is 'NTAG2xx':
            print('Chip is NTAG')
            buf = [0xA2, addr]
            buf += data
            
            print('my own crc function')
            print(rfid_get_crc(buf,6)/256)
            print(rfid_get_crc(buf,6) - rfid_get_crc(buf,6)/255)
            buf += self._crc(buf)
            print('buf')
            print(buf)
            (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
            print(stat)
            print(recv)
            print(bits)
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR
            #else:
                buf = [0xA2, addr]
                for i in range(16):
                    buf.append(data[i])
                    #print(i)
                buf += self._crc(buf)
                print('2nd Buffer')
                print(buf)
                (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
                if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                    stat = self.ERR
        else:
            buf = [0xA0, addr]
            
            
            print(buf)
            #print('my own crc function')
            #print(rfid_get_crc(buf,18))
            
            buf += self._crc(buf)
            
            print('buf')
            print(buf)
            
            (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR
            else:
                buf = []
                for i in range(16):
                    buf.append(data[i])
                    #print(i)
                buf += self._crc(buf)
                print('buf')
                print(buf)
                (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
                if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                    stat = self.ERR
                
#             if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
#                 stat = self.ERR
#             else:
#                 buf = []
#                 for i in range(16):
#                     buf.append(data[i])
#                     #print(i)
#                 buf += self._crc(buf)
#                 print(buf)
#                 (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
#                 if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
#                     stat = self.ERR

        return stat

    def SelfTest(self): # page 82
        self.reset()
        self._wreg(_REG_FIFO_DATA, bytes([25]))
        self._wreg(_REG_AUTO_TEST, 0x09)
        self._wreg(_REG_FIFO_DATA, 0x00)
        self._wreg(_REG_COMMAND, _CMD_CALC_CRC)
        sleep_ms(1000)
        test_output = self.i2c.readfrom_mem(self.addr, _REG_FIFO_DATA, 64)
        #print('test output')
        #print(test_output)
        version = self.i2c.readfrom_mem(self.addr, _REG_VERSION, 1)
        #print('version')
        #print(version)
        
    def readID(self):
        stat, bits = self.request(_TAG_CMD_REQIDL)
        return stat, bits
    
    def SelectTagSN(self):
        valid_uid=[]
        (status,uid)= self.anticoll(_TAG_CMD_ANTCOL1)
        #print("Select Tag 1:",self.tohexstring(uid))
        if status != self.OK:
            return  (self.ERR,[])
        
        #if self.DEBUG:   print("anticol(1) {}".format(uid))
        if self.PcdSelect(uid,_TAG_CMD_ANTCOL1) == 0:
            return (self.ERR,[])
        #if self.DEBUG:   print("pcdSelect(1) {}".format(uid))
        
        #check if first byte is 0x88
        if uid[0] == 0x88 :
            #ok we have another type of card
            valid_uid.extend(uid[1:4])
            (status,uid)=self.anticoll(_TAG_CMD_ANTCOL2)
            #print("Select Tag 2:",self.tohexstring(uid))
            if status != self.OK:
                return (self.ERR,[])
            #if self.DEBUG: print("Anticol(2) {}".format(uid))
            rtn =  self.PcdSelect(uid,_TAG_CMD_ANTCOL2)
            #if self.DEBUG: print("pcdSelect(2) return={} uid={}".format(rtn,uid))
            if rtn == 0:
                return (self.ERR,[])
            #if self.DEBUG: print("PcdSelect2() {}".format(uid))
            #now check again if uid[0] is 0x88
            if uid[0] == 0x88 :
                valid_uid.extend(uid[1:4])
                (status , uid) = self.anticoll(_TAG_CMD_ANTCOL3)
                #print("Select Tag 3:",self.tohexstring(uid))
                if status != self.OK:
                    return (self.ERR,[])
                #if self.DEBUG: print("Anticol(3) {}".format(uid))
                if self.MFRC522_PcdSelect(uid,_TAG_CMD_ANTCOL3) == 0:
                    return (self.ERR,[])
                #if self.DEBUG: print("PcdSelect(3) {}".format(uid))
        valid_uid.extend(uid[0:5])
        # if we are here than the uid is ok
        # let's remove the last BYTE whic is the XOR sum
        
        return (self.OK , valid_uid[:len(valid_uid)-1])
        #return (self.OK , valid_uid)
    
    def PcdSelect(self, serNum,anticolN):
        backData = []
        buf = []
        buf.append(anticolN)
        buf.append(0x70)
        #i = 0
        ###xorsum=0;
        for i in serNum:
            buf.append(i)
        #while i<5:
        #    buf.append(serNum[i])
        #    i = i + 1
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
        return {'present':_present, 'ATQA':ATQA}

    def readTagID(self):
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
        return {'success':_success, 'id_integers':id, 'id_formatted':id_formatted.upper()}
    
    def readTagData(self, register, data_type, tag_chip):
        tag_data = None
        auth_result = 0
        while tag_data is None:
            (stat, tag_type) = self.request(_TAG_CMD_REQIDL)
            if stat == self.OK:
                (stat, raw_uid) = self.anticoll()
                if stat == self.OK:
                    if self.select_tag(raw_uid) == self.OK:
                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                        if tag_chip is not 'NTAG2xx':
                            auth_result = self.auth(self.AUTHENT1A, register, key, raw_uid)
                        if (auth_result == self.OK) or tag_chip == 'NTAG2xx':
                            if self.DEBUG: print("made it here {}".format(self.OK))
                            raw_data = self.read(register)
                            if raw_data is not None:
                                if self.DEBUG: print("made it here1 {}".format(self.OK))
                                if data_type is 'text':
                                    tag_data = "".join(chr(x) for x in raw_data)
                                if data_type is 'ints':
                                    tag_data = raw_data
                            self.stop_crypto1()
                            return tag_data
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")
            sleep_ms(10)
            
    def writeTagData(self, data, register, tag_chip):
        while True:
            auth_result = 0
            (stat, tag_type) = self.request(_TAG_CMD_REQIDL)

            if stat == self.OK:
                (stat, raw_uid) = self.anticoll()

                if stat == self.OK:
                    if self.select_tag(raw_uid) == self.OK:

                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                        if tag_chip is not 'NTAG2xx':
                            auth_result = self.auth(self.AUTHENT1A, 8, key, raw_uid)
                        if (auth_result == self.OK) or tag_chip == 'NTAG2xx':
                            if self.DEBUG: print("made it here {}".format(self.OK))
                            if type(data) is str:
                                buffer_size = 16
                                if tag_chip is 'NTAG2xx':
                                    buffer_size = 4
                                if len(data) > buffer_size:
                                    data = data[:buffer_size]
                                while len(data) < buffer_size:
                                    data = data + " "
                                #data_encoded = data.encode()
                                data_byte_array = [ord(x) for x in list(data)]
                            stat = self.write(register, data_byte_array, tag_chip)
                            self.stop_crypto1()
                            if stat == self.OK:
                                return True # Data written to tag
                            else:
                                print("Failed to write data to tag")
                                return False
                        else:
                            print("Authentication error")
                            return False
                    else:
                        print("Failed to select tag")
                        return False

