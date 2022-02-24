_I='microbit'
_H='present'
_G=None
_F='type'
_E='id_integers'
_D=True
_C='id_formatted'
_B='success'
_A=False
from PiicoDev_Unified import *
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
_SYSNAME=os.uname().sysname
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
_TAG_AUTH_KEY_A=96
_CLASSIC_KEY=[255,255,255,255,255,255]
class PiicoDev_RFID:
	OK=1;NOTAGERR=2;ERR=3
	def __init__(self,bus=_G,freq=_G,sda=_G,scl=_G,address=_I2C_ADDRESS,suppress_warnings=_A):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl);self.address=address;self._tag_present=_A;self._read_tag_id_success=_A;self.reset();sleep_ms(50);self._wreg(_REG_T_MODE,128);self._wreg(_REG_T_PRESCALER,169);self._wreg(_REG_T_RELOAD_HI,3);self._wreg(_REG_T_RELOAD_LO,232);self._wreg(_REG_TX_ASK,64);self._wreg(_REG_MODE,61);self._wreg(_REG_DIV_I_EN,128);self._wreg(_REG_COM_I_EN,32);self.antenna_on()
		if _SYSNAME==_I and not suppress_warnings:print('This library can only be used to get tag IDs.\nAdvanced methods such as reading and wring to tag memory are not available on Micro:bit due to the limited storage available.\nTo run advanced methods, use a Raspberry Pi Pico instead of Micro:bit.\nTo suppress this warning, initialise with PiicoDev_RFID(suppress_warnings=True)\n')
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
	def _request(self,mode):
		self._wreg(_REG_BIT_FRAMING,7);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,[mode])
		if(stat!=self.OK)|(bits!=16):stat=self.ERR
		return stat,bits
	def _anticoll(self,anticolN=_TAG_CMD_ANTCOL1):
		ser_chk=0;ser=[anticolN,32];self._wreg(_REG_BIT_FRAMING,0);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,ser)
		if stat==self.OK:
			if len(recv)==5:
				for i in range(4):ser_chk=ser_chk^recv[i]
				if ser_chk!=recv[4]:stat=self.ERR
			else:stat=self.ERR
		return stat,recv
	def _selectTag(self,serNum,anticolN):
		backData=[];buf=[];buf.append(anticolN);buf.append(112)
		for i in serNum:buf.append(i)
		pOut=self._crc(buf);buf.append(pOut[0]);buf.append(pOut[1]);status,backData,backLen=self._tocard(12,buf)
		if status==self.OK and backLen==24:return 1
		else:return 0
	def _readTagID(self):
		result={_B:_A,_E:[],_C:'',_F:''};valid_uid=[];status,uid=self._anticoll(_TAG_CMD_ANTCOL1)
		if status!=self.OK:return result
		if self._selectTag(uid,_TAG_CMD_ANTCOL1)==0:return result
		if uid[0]==136:
			valid_uid.extend(uid[1:4]);status,uid=self._anticoll(_TAG_CMD_ANTCOL2)
			if status!=self.OK:return result
			rtn=self._selectTag(uid,_TAG_CMD_ANTCOL2)
			if rtn==0:return result
			if uid[0]==136:
				valid_uid.extend(uid[1:4]);status,uid=self._anticoll(_TAG_CMD_ANTCOL3)
				if status!=self.OK:return result
		valid_uid.extend(uid[0:5]);id_formatted='';id=valid_uid[:len(valid_uid)-1]
		for i in range(0,len(id)):
			if i>0:id_formatted=id_formatted+':'
			if id[i]<16:id_formatted=id_formatted+'0'
			id_formatted=id_formatted+hex(id[i])[2:]
		type='ntag'
		if len(id)==4:type='classic'
		return{_B:_D,_E:id,_C:id_formatted.upper(),_F:type}
	def _detectTag(self):
		stat,ATQA=self._request(_TAG_CMD_REQIDL);_present=_A
		if stat is self.OK:_present=_D
		self._tag_present=_present;return{_H:_present,'ATQA':ATQA}
	def reset(self):self._wreg(_REG_COMMAND,_CMD_SOFT_RESET)
	def antennaOn(self):
		if~(self._rreg(_REG_TX_CONTROL)&3):self._sflags(_REG_TX_CONTROL,131)
	def antennaOff(self):
		if not~(self._rreg(_REG_TX_CONTROL)&3):self._cflags(_REG_TX_CONTROL,b'\x03')
	def readTagID(self):
		detect_tag_result=self._detectTag()
		if detect_tag_result[_H]is _A:detect_tag_result=self._detectTag()
		if detect_tag_result[_H]:
			read_tag_id_result=self._readTagID()
			if read_tag_id_result[_B]:self._read_tag_id_success=_D;return{_B:read_tag_id_result[_B],_E:read_tag_id_result[_E],_C:read_tag_id_result[_C],_F:read_tag_id_result[_F]}
		self._read_tag_id_success=_A;return{_B:_A,_E:[0],_C:'',_F:''}
	def readID(self):tagId=self.readTagID();return tagId[_C]
	def tagPresent(self):id=self.readTagID();return id[_B]
	if _SYSNAME!=_I:
		try:from PiicoDev_RFID_Expansion import _classicSelectTag,_classicAuth,_classicStopCrypto,_writePageNtag,_classicWrite,_writeClassicRegister,_read,_readClassicData,_writeNumberToNtag,_writeNumberToClassic,writeNumber,readNumber,_writeTextToNtag,_writeTextToClassic,writeText,_readTextFromNtag,_readTextFromClassic,readText,writeLink
		except:print('Install PiicoDev_RFID_Expansion.py for full functionality')