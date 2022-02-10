_N='Slot must be between 0 and 35'
_M='Failed to select tag'
_L='Authentication error'
_K='\x00'
_J='present'
_I='id_integers'
_H='id_formatted'
_G='classic'
_F='ntag'
_E=None
_D='success'
_C=True
_B='type'
_A=False
from PiicoDev_Unified import *
import struct
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
_I2C_ADDRESS=44
_REG_COMMAND=1
_REG_COM_I_EN=2
_REG_COM_IRQ=4
_REG_DIV_IRQ=5
_REG_ERROR=6
_REG_STATUS_1=7
_REG_STATUS_2=8
_REG_FIFO_DATA=9
_REG_FIFO_LEVEL=10
_REG_CONTROL=12
_REG_BIT_FRAMING=13
_REG_MODE=17
_REG_TX_CONTROL=20
_REG_TX_ASK=21
_REG_CRC_RESULT_MSB=33
_REG_CRC_RESULT_LSB=34
_REG_T_MODE=42
_REG_T_PRESCALER=43
_REG_T_RELOAD_HI=44
_REG_T_RELOAD_LO=45
_REG_AUTO_TEST=54
_REG_VERSION=55
_CMD_IDLE=0
_CMD_CALC_CRC=3
_CMD_TRANCEIVE=12
_CMD_MF_AUTHENT=14
_CMD_SOFT_RESET=15
_TAG_CMD_REQIDL=38
_TAG_CMD_REQALL=82
_TAG_CMD_ANTCOL1=147
_TAG_CMD_ANTCOL2=149
_TAG_CMD_ANTCOL3=151
_NTAG_NO_BYTES_PER_PAGE=4
_NTAG_PAGE_ADR_MIN=4
_NTAG_PAGE_ADR_MAX=39
_TAG_AUTH_KEY_A=96
_CLASSIC_KEY=[255,255,255,255,255,255]
_CLASSIC_NO_BYTES_PER_REG=16
_CLASSIC_ADR=[1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26,28,29,30,32,33,34,36,37,38,40,41,42,44,45,46,48]
_SLOT_NO_MIN=0
_SLOT_NO_MAX=35
def _readBit(x,n):return x&1<<n!=0
def _setBit(x,n):return x|1<<n
def _clearBit(x,n):return x&~(1<<n)
def _writeBit(x,n,b):
	if b==0:return _clearBit(x,n)
	else:return _setBit(x,n)
def _writeCrumb(x,n,c):x=_writeBit(x,n,_readBit(c,0));return _writeBit(x,n+1,_readBit(c,1))
class PiicoDev_RFID:
	OK=1;NOTAGERR=2;ERR=3
	def __init__(self,bus=_E,freq=_E,sda=_E,scl=_E,address=_I2C_ADDRESS):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl);self.address=address;self._tag_present=_A;self._read_tag_id_success=_A;self.init()
	def _wreg(self,reg,val):self.i2c.writeto_mem(self.address,reg,bytes([val]))
	def _wfifo(self,reg,val):self.i2c.writeto_mem(self.address,reg,bytes(val))
	def _rreg(self,reg):val=self.i2c.readfrom_mem(self.address,reg,1);return val[0]
	def _sflags(self,reg,mask):current_value=self._rreg(reg);self._wreg(reg,current_value|mask)
	def _cflags(self,reg,mask):self._wreg(reg,self._rreg(reg)&~ mask)
	def _tocard(self,cmd,send):
		recv=[];bits=irq_en=wait_irq=n=0;stat=self.ERR
		if cmd==_CMD_MF_AUTHENT:irq_en=18;wait_irq=16
		elif cmd==_CMD_TRANCEIVE:irq_en=119;wait_irq=48
		self._wreg(_REG_COMMAND,_CMD_IDLE);self._wreg(_REG_COM_IRQ,127);self._sflags(_REG_FIFO_LEVEL,128);self._wfifo(_REG_FIFO_DATA,send)
		if cmd==_CMD_TRANCEIVE:self._sflags(_REG_BIT_FRAMING,0)
		self._wreg(_REG_COMMAND,cmd)
		if cmd==_CMD_TRANCEIVE:self._sflags(_REG_BIT_FRAMING,128)
		i=20000
		while _C:
			n=self._rreg(_REG_COM_IRQ);i-=1
			if n&wait_irq:break
			if n&1:break
			if i==0:break
		self._cflags(_REG_BIT_FRAMING,128)
		if i:
			if self._rreg(_REG_ERROR)&27==0:
				stat=self.OK
				if n&irq_en&1:stat=self.NOTAGERR
				elif cmd==_CMD_TRANCEIVE:
					n=self._rreg(_REG_FIFO_LEVEL);lbits=self._rreg(_REG_CONTROL)&7
					if lbits!=0:bits=(n-1)*8+lbits
					else:bits=n*8
					if n==0:n=1
					elif n>16:n=16
					for _ in range(n):recv.append(self._rreg(_REG_FIFO_DATA))
			else:stat=self.ERR
		return stat,recv,bits
	def _crc(self,data):
		self._wreg(_REG_COMMAND,_CMD_IDLE);self._cflags(_REG_DIV_IRQ,4);self._sflags(_REG_FIFO_LEVEL,128)
		for c in data:self._wreg(_REG_FIFO_DATA,c)
		self._wreg(_REG_COMMAND,_CMD_CALC_CRC);i=255
		while _C:
			n=self._rreg(_REG_DIV_IRQ);i-=1
			if not(i!=0 and not n&4):break
		self._wreg(_REG_COMMAND,_CMD_IDLE);return[self._rreg(_REG_CRC_RESULT_LSB),self._rreg(_REG_CRC_RESULT_MSB)]
	def init(self):self.reset();sleep_ms(50);self._wreg(_REG_T_MODE,128);self._wreg(_REG_T_PRESCALER,169);self._wreg(_REG_T_RELOAD_HI,3);self._wreg(_REG_T_RELOAD_LO,232);self._wreg(_REG_TX_ASK,64);self._wreg(_REG_MODE,61);self.antenna_on()
	def reset(self):self._wreg(_REG_COMMAND,_CMD_SOFT_RESET)
	def antenna_on(self,on=_C):
		if on and~(self._rreg(_REG_TX_CONTROL)&3):self._sflags(_REG_TX_CONTROL,131)
		else:self._cflags(_REG_TX_CONTROL,b'\x03')
	def request(self,mode):
		self._wreg(_REG_BIT_FRAMING,7);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,[mode])
		if(stat!=self.OK)|(bits!=16):stat=self.ERR
		return stat,bits
	def anticoll(self,anticolN=_TAG_CMD_ANTCOL1):
		ser_chk=0;ser=[anticolN,32];self._wreg(_REG_BIT_FRAMING,0);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,ser)
		if stat==self.OK:
			if len(recv)==5:
				for i in range(4):ser_chk=ser_chk^recv[i]
				if ser_chk!=recv[4]:stat=self.ERR
			else:stat=self.ERR
		return stat,recv
	def select_tag(self,ser):buf=[147,112]+ser[:5];buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf);return self.OK if stat==self.OK and bits==24 else self.ERR
	def auth(self,mode,addr,sect,ser):return self._tocard(_CMD_MF_AUTHENT,[mode,addr]+sect+ser[:4])[0]
	def stop_crypto1(self):self._cflags(_REG_STATUS_2,8)
	def read(self,addr):data=[48,addr];data+=self._crc(data);stat,recv,_=self._tocard(_CMD_TRANCEIVE,data);return recv if stat==self.OK else _E
	def classicWrite(self,addr,data):
		buf=[160,addr];buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
		if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		else:
			buf=[]
			for i in range(_CLASSIC_NO_BYTES_PER_REG):buf.append(data[i])
			buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
			if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		return stat
	def writePageNtag(self,page,data):buf=[162,page];buf+=data;buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf);return stat
	def SelfTest(self):self.reset();self._wreg(_REG_FIFO_DATA,bytes([25]));self._wreg(_REG_AUTO_TEST,9);self._wreg(_REG_FIFO_DATA,0);self._wreg(_REG_COMMAND,_CMD_CALC_CRC);sleep_ms(1000);test_output=self.i2c.readfrom_mem(self.addr,_REG_FIFO_DATA,64);version=self.i2c.readfrom_mem(self.addr,_REG_VERSION,1)
	def readID(self):stat,bits=self.request(_TAG_CMD_REQIDL);return stat,bits
	def SelectTagSN(self):
		valid_uid=[];status,uid=self.anticoll(_TAG_CMD_ANTCOL1)
		if status!=self.OK:return self.ERR,[]
		if self.PcdSelect(uid,_TAG_CMD_ANTCOL1)==0:return self.ERR,[]
		if uid[0]==136:
			valid_uid.extend(uid[1:4]);status,uid=self.anticoll(_TAG_CMD_ANTCOL2)
			if status!=self.OK:return self.ERR,[]
			rtn=self.PcdSelect(uid,_TAG_CMD_ANTCOL2)
			if rtn==0:return self.ERR,[]
			if uid[0]==136:
				valid_uid.extend(uid[1:4]);status,uid=self.anticoll(_TAG_CMD_ANTCOL3)
				if status!=self.OK:return self.ERR,[]
				if self.MFRC522_PcdSelect(uid,_TAG_CMD_ANTCOL3)==0:return self.ERR,[]
		valid_uid.extend(uid[0:5]);return self.OK,valid_uid[:len(valid_uid)-1]
	def PcdSelect(self,serNum,anticolN):
		backData=[];buf=[];buf.append(anticolN);buf.append(112)
		for i in serNum:buf.append(i)
		pOut=self._crc(buf);buf.append(pOut[0]);buf.append(pOut[1]);status,backData,backLen=self._tocard(12,buf)
		if status==self.OK and backLen==24:return 1
		else:return 0
	def detectTag(self):
		stat,ATQA=self.request(_TAG_CMD_REQIDL);_present=_A
		if stat is self.OK:_present=_C
		self._tag_present=_present;return{_J:_present,'ATQA':ATQA}
	def _readTagID(self):
		stat,id=self.SelectTagSN();_success=_C
		if stat is self.OK:_success=_C
		id_formatted=''
		for i in range(0,len(id)):
			if i>0:id_formatted=id_formatted+':'
			if id[i]<16:id_formatted=id_formatted+'0'
			id_formatted=id_formatted+hex(id[i])[2:]
		type=_F
		if len(id)==4:type=_G
		return{_D:_success,_I:id,_H:id_formatted.upper(),_B:type}
	def readClassicData(self,register):
		tag_data=_E;auth_result=0
		while tag_data is _E:
			stat,tag_type=self.request(_TAG_CMD_REQIDL)
			if stat==self.OK:
				stat,raw_uid=self.anticoll()
				if stat==self.OK:
					if self.select_tag(raw_uid)==self.OK:
						auth_result=self.auth(_TAG_AUTH_KEY_A,register,_CLASSIC_KEY,raw_uid)
						if auth_result==self.OK:tag_data=self.read(register);self.stop_crypto1();return tag_data
						else:print(_L)
					else:print(_M)
			sleep_ms(10)
	def writeClassicRegister(self,register,data_byte_array):
		while _C:
			auth_result=0;stat,tag_type=self.request(_TAG_CMD_REQIDL)
			if stat==self.OK:
				stat,raw_uid=self.anticoll()
				if stat==self.OK:
					if self.select_tag(raw_uid)==self.OK:
						auth_result=self.auth(_TAG_AUTH_KEY_A,register,_CLASSIC_KEY,raw_uid)
						if auth_result==self.OK:
							stat=self.classicWrite(register,data_byte_array);self.stop_crypto1()
							if stat==self.OK:return _C
							else:print('Failed to write data to tag');return _A
						else:print(_L);return _A
					else:print(_M);return _A
	def writeNumberToNtag(self,bytes_number,slot=0):
		tag_write_success=_A;assert slot>=_SLOT_NO_MIN and slot<=_SLOT_NO_MAX,_N;page_adr_min=4;stat=self.writePageNtag(page_adr_min+slot,bytes_number);tag_write_success=_A
		if stat==self.OK:tag_write_success=_C
		return tag_write_success
	def writeNumberToClassic(self,bytes_number,slot=0):
		assert slot>=_SLOT_NO_MIN and slot<=_SLOT_NO_MAX,_N
		while len(bytes_number)<_CLASSIC_NO_BYTES_PER_REG:bytes_number.append(0)
		tag_write_success=self.writeClassicRegister(_CLASSIC_ADR[slot],bytes_number);return tag_write_success
	def readTextFromNtag(self):
		page_adr=_NTAG_PAGE_ADR_MIN;total_string=''
		while page_adr<=_NTAG_PAGE_ADR_MAX:
			raw_data=self.read(page_adr);print(raw_data);page_text=''.join((chr(x)for x in raw_data));total_string=total_string+page_text
			if 0 in raw_data:substring=total_string.split(_K);return substring[0]
			page_adr=page_adr+_NTAG_NO_BYTES_PER_PAGE
		return total_string
	def readTextFromClassic(self):
		x=0;total_string=''
		for slot in range(9):
			reg_data=self.readClassicData(_CLASSIC_ADR[slot]);reg_text=''.join((chr(x)for x in reg_data));total_string=total_string+reg_text
			if 0 in reg_data:substring=total_string.split(_K);return substring[0]
		return total_string
	def writeTextToNtag(self,text):
		buffer_start=0
		for page_adr in range(_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX):
			data_chunk=text[buffer_start:buffer_start+_NTAG_NO_BYTES_PER_PAGE];buffer_start=buffer_start+_NTAG_NO_BYTES_PER_PAGE;data_byte_array=[ord(x)for x in list(data_chunk)]
			while len(data_byte_array)<_NTAG_NO_BYTES_PER_PAGE:data_byte_array.append(0)
			tag_write_success=self.writePageNtag(page_adr,data_byte_array)
			if 0 in data_byte_array:return tag_write_success
		return tag_write_success
	def writeTextToClassic(self,text):
		buffer_start=0;x=0
		for slot in range(9):
			data_chunk=text[buffer_start:buffer_start+_CLASSIC_NO_BYTES_PER_REG];buffer_start=buffer_start+_CLASSIC_NO_BYTES_PER_REG;data_byte_array=[ord(x)for x in list(data_chunk)]
			while len(data_byte_array)<_CLASSIC_NO_BYTES_PER_REG:data_byte_array.append(0)
			tag_write_success=self.writeClassicRegister(_CLASSIC_ADR[slot],data_byte_array)
			if 0 in data_byte_array:return tag_write_success
		return tag_write_success
	def writeURL(self,url):is_ndef_message=chr(3);ndef_length=chr(len(url)+5);ndef_record_header=chr(209);ndef_type_length=chr(1);ndef_payload_length=chr(len(url)+1);is_uri_record=chr(85);record_type_indicator=chr(4);tlv_terminator=chr(254);ndef=is_ndef_message+ndef_length+ndef_record_header+ndef_type_length+ndef_payload_length+is_uri_record+record_type_indicator+url+tlv_terminator;print(ndef);success=self.writeText(ndef);return success
	def readTagID(self):
		detect_tag_result=self.detectTag()
		if detect_tag_result[_J]is _A:detect_tag_result=self.detectTag()
		if detect_tag_result[_J]:
			read_tag_id_result=self._readTagID()
			if read_tag_id_result[_D]:self._read_tag_id_success=_C;return{_D:read_tag_id_result[_D],_I:read_tag_id_result[_I],_H:read_tag_id_result[_H],_B:read_tag_id_result[_B]}
		self._read_tag_id_success=_A;return{_D:_A,_I:[0],_H:'',_B:''}
	def writeText(self,text):
		success=_A;maximum_characters=144;text=text+_K;read_tag_id_result=self.readTagID()
		if read_tag_id_result[_B]==_F:success=self.writeTextToNtag(text)
		if read_tag_id_result[_B]==_G:success=self.writeTextToClassic(text)
		return success
	def writeNumber(self,number,slot=35):
		success=_A;bytearray_number=bytearray(struct.pack('l',number));read_tag_id_result=self.readTagID()
		while read_tag_id_result[_D]is _A:read_tag_id_result=self.readTagID()
		if read_tag_id_result[_D]:
			if read_tag_id_result[_B]==_F:
				success=self.writeNumberToNtag(bytearray_number,slot)
				while success is _A:success=self.writeNumberToNtag(bytearray_number,slot)
			if read_tag_id_result[_B]==_G:
				success=self.writeNumberToClassic(bytearray_number,slot)
				while success is _A:success=self.writeNumberToClassic(bytearray_number,slot)
		return success
	def readText(self):
		text='';read_tag_id_result=self.readTagID()
		while read_tag_id_result[_D]is _A:read_tag_id_result=self.readTagID()
		if read_tag_id_result[_B]==_F:text=self.readTextFromNtag()
		if read_tag_id_result[_B]==_G:text=self.readTextFromClassic()
		return text
	def readNumber(self,slot=35):
		bytearray_number=_E;read_tag_id_result=self.readTagID()
		while read_tag_id_result[_D]is _A:read_tag_id_result=self.readTagID()
		if read_tag_id_result[_B]==_F:page_address=4;bytearray_number=self.read(page_address+slot)
		if read_tag_id_result[_B]==_G:bytearray_number=self.readClassicData(_CLASSIC_ADR[slot])
		try:number=struct.unpack('l',bytes(bytearray_number));number=number[0];return number
		except:print('Error reading card');return 0
	def readID(self):tagId=self.readTagID();return tagId[_H]
	def tagPresent(self):id=self.readTagID();return id[_D]