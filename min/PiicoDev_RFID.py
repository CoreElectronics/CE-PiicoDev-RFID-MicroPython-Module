_P='Authentication error'
_O='made it here1 {}'
_N='Failed to select tag'
_M='ints'
_L='text'
_K='made it here {}'
_J='present'
_I='id_formatted'
_H='id_integers'
_G='classic'
_F='ntag'
_E='success'
_D=True
_C='type'
_B=None
_A=False
from PiicoDev_Unified import *
import struct
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
_I2C_ADDRESS=44
_REG_COMMAND=1
_REG_COM_I_EN=2
_REG_DIV_I_EN=3
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
def _readBit(x,n):return x&1<<n!=0
def _setBit(x,n):return x|1<<n
def _clearBit(x,n):return x&~(1<<n)
def _writeBit(x,n,b):
	if b==0:return _clearBit(x,n)
	else:return _setBit(x,n)
def _writeCrumb(x,n,c):x=_writeBit(x,n,_readBit(c,0));return _writeBit(x,n+1,_readBit(c,1))
class PiicoDev_RFID:
	DEBUG=_A;OK=10;NOTAGERR=31;ERR=42;AUTHENT1A=96;AUTHENT1B=97
	def __init__(self,bus=_B,freq=_B,sda=_B,scl=_B,addr=_I2C_ADDRESS):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl);self.addr=addr;self.init()
	def _wreg(self,reg,val):self.i2c.writeto_mem(self.addr,reg,bytes([val]))
	def _wfifo(self,reg,val):self.i2c.writeto_mem(self.addr,reg,bytes(val))
	def _rreg(self,reg):val=self.i2c.readfrom_mem(self.addr,reg,1);return val[0]
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
		while _D:
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
		while _D:
			n=self._rreg(_REG_DIV_IRQ);i-=1
			if not(i!=0 and not n&4):break
		self._wreg(_REG_COMMAND,_CMD_IDLE);return[self._rreg(_REG_CRC_RESULT_LSB),self._rreg(_REG_CRC_RESULT_MSB)]
	def init(self):self.reset();sleep_ms(50);self._wreg(_REG_T_MODE,128);self._wreg(_REG_T_PRESCALER,169);self._wreg(_REG_T_RELOAD_HI,3);self._wreg(_REG_T_RELOAD_LO,232);self._wreg(_REG_TX_ASK,64);self._wreg(_REG_MODE,61);self.antenna_on()
	def reset(self):self._wreg(_REG_COMMAND,_CMD_SOFT_RESET)
	def antenna_on(self,on=_D):
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
	def read(self,addr):data=[48,addr];data+=self._crc(data);stat,recv,_=self._tocard(_CMD_TRANCEIVE,data);return recv if stat==self.OK else _B
	def classicWrite(self,addr,data):
		buf=[160,addr];buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
		if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		else:
			buf=[]
			for i in range(16):buf.append(data[i])
			buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
			if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		return stat
	def nTAG2xxWrite(self,page,data):buf=[162,page];buf+=data;buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf);return stat
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
		if stat is self.OK:_present=_D
		return{_J:_present,'ATQA':ATQA}
	def _readTagID(self):
		stat,id=self.SelectTagSN();_success=_D
		if stat is self.OK:_success=_D
		id_formatted=''
		for i in range(0,len(id)):
			if i>0:id_formatted=id_formatted+':'
			if id[i]<16:id_formatted=id_formatted+'0'
			id_formatted=id_formatted+hex(id[i])[2:]
		type=_F
		if len(id)==4:type=_G
		return{_E:_success,_H:id,_I:id_formatted.upper(),_C:type}
	def readTagData(self,register,data_type,tag_chip):
		A='NTAG2xx';tag_data=_B;auth_result=0
		while tag_data is _B:
			stat,tag_type=self.request(_TAG_CMD_REQIDL)
			if stat==self.OK:
				stat,raw_uid=self.anticoll()
				if stat==self.OK:
					if self.select_tag(raw_uid)==self.OK:
						if tag_chip is not A:key=[255,255,255,255,255,255];auth_result=self.auth(self.AUTHENT1A,register,key,raw_uid)
						if auth_result==self.OK or tag_chip==A:
							if self.DEBUG:print(_K.format(self.OK))
							raw_data=self.read(register)
							if raw_data is not _B:
								if self.DEBUG:print(_O.format(self.OK))
								if data_type is _L:tag_data=''.join((chr(x)for x in raw_data))
								if data_type is _M:tag_data=raw_data
							self.stop_crypto1();return tag_data
						else:print(_P)
					else:print(_N)
			sleep_ms(10)
	def readNTAG213Data(self,page,data_type,tag_chip):
		tag_data=_B;auth_result=0
		while tag_data is _B:
			stat,tag_type=self.request(_TAG_CMD_REQIDL)
			if stat==self.OK:
				stat,raw_uid=self.anticoll()
				if stat==self.OK:
					if self.select_tag(raw_uid)==self.OK:
						if self.DEBUG:print(_K.format(self.OK))
						raw_data=self.read(page)
						if raw_data is not _B:
							if self.DEBUG:print(_O.format(self.OK))
							if data_type is _L:tag_data=''.join((chr(x)for x in raw_data))
							if data_type is _M:tag_data=raw_data
						return tag_data
					else:print(_N)
			sleep_ms(10)
	def writeTagDataNonNTAG(self,register,data_byte_array):
		while _D:
			auth_result=0;stat,tag_type=self.request(_TAG_CMD_REQIDL)
			if stat==self.OK:
				stat,raw_uid=self.anticoll()
				if stat==self.OK:
					if self.select_tag(raw_uid)==self.OK:
						key=[255,255,255,255,255,255];auth_result=self.auth(self.AUTHENT1A,register,key,raw_uid)
						if auth_result==self.OK:
							if self.DEBUG:print(_K.format(self.OK))
							stat=self.classicWrite(register,data_byte_array);self.stop_crypto1()
							if stat==self.OK:return _D
							else:print('Failed to write data to tag');return _A
						else:print(_P);return _A
					else:print(_N);return _A
	def writeTextToNtag(self,text):
		data=text;page_adr_min=4;page_adr_max=39;bytes_per_page=4;buffer_start=0;bytes_per_page=4;page_adr=page_adr_min
		while page_adr<=page_adr_max:
			data_chunk=data[buffer_start:buffer_start+bytes_per_page];buffer_start=buffer_start+bytes_per_page;data_byte_array=[ord(x)for x in list(data_chunk)];stat=self.nTAG2xxWrite(page_adr,data_byte_array);tag_write_success=_A
			if stat==self.OK:tag_write_success=_D
			page_adr=page_adr+1
		return tag_write_success
	def writeNumberToNtag(self,bytes_number):
		data=bytes_number;page_adr_min=4;page_adr_max=4;bytes_per_page=4;buffer_start=0;bytes_per_page=4;page_adr=page_adr_min
		while page_adr<=page_adr_max:
			data_chunk=data[buffer_start:buffer_start+bytes_per_page];buffer_start=buffer_start+bytes_per_page;data_byte_array=bytes_number;stat=self.nTAG2xxWrite(page_adr,data_byte_array);tag_write_success=_A
			if stat==self.OK:tag_write_success=_D
			page_adr=page_adr+1
		return tag_write_success
	def readTextFromNtag(self):
		page_adr_min=4;page_adr_max=39;bytes_per_page=4;buffer_start=0;bytes_per_page=4;page_adr=page_adr_min;total_string=''
		while page_adr<=page_adr_max:raw_data=self.read(page_adr);page_text=''.join((chr(x)for x in raw_data));total_string=total_string+page_text;page_adr=page_adr+bytes_per_page
		return total_string
	def readNumberFromNtag(self):page_adr=4;raw_data=self.read(page_adr);return raw_data
	def readNumberFromClassic(self):
		adr_list=[1];tag_chip='';buffer_start=0;bytes_per_adr=16;x=0;total_string=''
		for address in adr_list:raw_data=self.readTagData(address,_M,tag_chip)
		return raw_data
	def writeTextToClassic(self,text):
		data=text;adr_list=[1,2,4,5,6,8,9,10,12];tag_chip='';buffer_start=0;bytes_per_adr=16;x=0
		for address in adr_list:data_chunk=data[buffer_start:buffer_start+bytes_per_adr];buffer_start=buffer_start+bytes_per_adr;data_byte_array=[ord(x)for x in list(data_chunk)];tag_write_success=self.writeTagDataNonNTAG(address,data_byte_array)
		return tag_write_success
	def writeNumberToClassic(self,bytes_number):
		while len(bytes_number)<16:bytes_number.append(0)
		adr_list=[1];tag_chip='';buffer_start=0;bytes_per_adr=16;x=0
		for address in adr_list:data_chunk=bytes_number[buffer_start:buffer_start+bytes_per_adr];buffer_start=buffer_start+bytes_per_adr;data_byte_array=bytes_number;tag_write_success=self.writeTagDataNonNTAG(address,data_byte_array)
		return tag_write_success
	def readTextFromClassic(self):
		adr_list=[1,2,4,5,6,8,9,10,12];tag_chip='';buffer_start=0;bytes_per_adr=16;x=0;total_string=''
		for address in adr_list:reg_text=self.readTagData(address,_L,tag_chip);total_string=total_string+reg_text
		return total_string
	def readTagID(self):
		detect_tag_result=self.detectTag()
		if detect_tag_result[_J]is _A:detect_tag_result=self.detectTag()
		if detect_tag_result[_J]:
			read_tag_id_result=self._readTagID()
			if read_tag_id_result[_E]:return{_E:read_tag_id_result[_E],_H:read_tag_id_result[_H],_I:read_tag_id_result[_I],_C:read_tag_id_result[_C]}
		return{_E:_A,_H:[0],_I:'',_C:''}
	def writeTextToTag(self,text):
		success=_A;maximum_characters=144
		while len(text)<maximum_characters:text=text+' '
		read_tag_id_result=self.readTagID()
		if read_tag_id_result[_C]==_F:success=self.writeTextToNtag(text)
		if read_tag_id_result[_C]==_G:success=self.writeTextToClassic(text)
		return success
	def writeNumberToTag(self,number):
		success=_A;bytearray_number=bytearray(struct.pack('l',number));read_tag_id_result=self.readTagID()
		while read_tag_id_result[_E]is _A:read_tag_id_result=self.readTagID()
		if read_tag_id_result[_E]:
			if read_tag_id_result[_C]==_F:
				success=self.writeNumberToNtag(bytearray_number)
				while success is _A:success=self.writeNumberToNtag(bytearray_number)
			if read_tag_id_result[_C]==_G:
				success=self.writeNumberToClassic(bytearray_number)
				while success is _A:success=self.writeNumberToClassic(bytearray_number)
		return success
	def readTextFromTag(self):
		text='';read_tag_id_result=self.readTagID()
		while read_tag_id_result[_E]is _A:read_tag_id_result=self.readTagID();print(read_tag_id_result)
		if read_tag_id_result[_C]==_F:text=self.readTextFromNtag()
		if read_tag_id_result[_C]==_G:text=self.readTextFromClassic()
		return text
	def readNumberFromTag(self):
		bytearray_number=_B;read_tag_id_result=self.readTagID()
		while read_tag_id_result[_E]is _A:read_tag_id_result=self.readTagID()
		if read_tag_id_result[_C]==_F:bytearray_number=self.readNumberFromNtag()
		if read_tag_id_result[_C]==_G:bytearray_number=self.readNumberFromClassic()
		try:number=struct.unpack('l',bytes(bytearray_number));number=number[0];return number
		except:print('Error reading card');return 0