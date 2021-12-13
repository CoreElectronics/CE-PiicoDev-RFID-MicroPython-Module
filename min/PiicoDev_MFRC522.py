_A=None
from PiicoDev_Unified import *
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
_REG_MODE=17
_REG_TX_CONTROL=20
_REG_TX_ASK=21
_REG_BIT_FRAMING=13
_REG_T_MODE=42
_REG_T_PRESCALER=43
_REG_T_RELOAD_HI=44
_REG_T_RELOAD_LO=45
_REG_AUTO_TEST=54
_REG_VERSION=55
_CMD_CALC_CRC=3
_CMD_TRANCEIVE=12
_CMD_SOFT_RESET=15
def _readBit(x,n):return x&1<<n!=0
def _setBit(x,n):return x|1<<n
def _clearBit(x,n):return x&~(1<<n)
def _writeBit(x,n,b):
	if b==0:return _clearBit(x,n)
	else:return _setBit(x,n)
def _writeCrumb(x,n,c):x=_writeBit(x,n,_readBit(c,0));return _writeBit(x,n+1,_readBit(c,1))
class PiicoDev_MFRC522:
	DEBUG=False;OK=0;NOTAGERR=1;ERR=2;REQIDL=38;REQALL=82;AUTHENT1A=96;AUTHENT1B=97;PICC_ANTICOLL1=147;PICC_ANTICOLL2=149;PICC_ANTICOLL3=151
	def __init__(self,bus=_A,freq=_A,sda=_A,scl=_A,addr=_I2C_ADDRESS):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl);self.addr=addr;self.init()
	def _wreg(self,reg,val):self.i2c.writeto_mem(self.addr,reg,bytes([val]))
	def _rreg(self,reg):val=self.i2c.readfrom_mem(self.addr,reg,1);return val[0]
	def _sflags(self,reg,mask):current_value=self._rreg(reg);self._wreg(reg,current_value|mask)
	def _cflags(self,reg,mask):self._wreg(reg,self._rreg(reg)&~ mask)
	def _tocard(self,cmd,send):
		recv=[];bits=irq_en=wait_irq=n=0;stat=self.ERR
		if cmd==14:irq_en=18;wait_irq=16
		elif cmd==_CMD_TRANCEIVE:irq_en=119;wait_irq=48
		self._wreg(_REG_COM_I_EN,irq_en|128);self._cflags(_REG_COM_IRQ,128);self._sflags(_REG_FIFO_LEVEL,128);self._wreg(_REG_COMMAND,0)
		for c in send:self._wreg(_REG_FIFO_DATA,c)
		self._wreg(_REG_COMMAND,cmd)
		if cmd==_CMD_TRANCEIVE:self._sflags(_REG_BIT_FRAMING,128)
		i=2000
		while True:
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
		self._cflags(_REG_DIV_IRQ,4);self._sflags(_REG_FIFO_LEVEL,128)
		for c in data:self._wreg(_REG_FIFO_DATA,c)
		self._wreg(_REG_COMMAND,3);i=255
		while True:
			n=self._rreg(_REG_DIV_IRQ);i-=1
			if not(i!=0 and not n&4):break
		return[self._rreg(34),self._rreg(33)]
	def init(self):sleep_ms(50);self._wreg(_REG_T_MODE,128);self._wreg(_REG_T_PRESCALER,169);self._wreg(_REG_T_RELOAD_HI,3);self._wreg(_REG_T_RELOAD_LO,232);self._wreg(_REG_TX_ASK,64);self._wreg(_REG_MODE,61);self.antenna_on();print('device initialised')
	def reset(self):self._wreg(_REG_COMMAND,_CMD_SOFT_RESET)
	def antenna_on(self,on=True):
		if on and~(self._rreg(_REG_TX_CONTROL)&3):self._sflags(_REG_TX_CONTROL,131)
		else:print('antenna code here 2');self._cflags(_REG_TX_CONTROL,b'\x03')
	def request(self,mode):
		self._wreg(_REG_BIT_FRAMING,7);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,[mode])
		if(stat!=self.OK)|(bits!=16):stat=self.ERR
		return stat,bits
	def anticoll(self):
		ser_chk=0;ser=[147,32];self._wreg(_REG_BIT_FRAMING,0);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,ser)
		if stat==self.OK:
			if len(recv)==5:
				for i in range(4):ser_chk=ser_chk^recv[i]
				if ser_chk!=recv[4]:stat=self.ERR
			else:stat=self.ERR
		return stat,recv
	def select_tag(self,ser):buf=[147,112]+ser[:5];buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf);return self.OK if stat==self.OK and bits==24 else self.ERR
	def auth(self,mode,addr,sect,ser):return self._tocard(14,[mode,addr]+sect+ser[:4])[0]
	def stop_crypto1(self):self._cflags(_REG_STATUS_2,8)
	def read(self,addr):data=[48,addr];data+=self._crc(data);stat,recv,_=self._tocard(_CMD_TRANCEIVE,data);return recv if stat==self.OK else _A
	def write(self,addr,data):
		buf=[160,addr];buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
		if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		else:
			buf=[]
			for i in range(16):buf.append(data[i])
			buf+=self._crc(buf);stat,recv,bits=self._tocard(_CMD_TRANCEIVE,buf)
			if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		return stat
	def SelfTest(self):self.reset();self._wreg(_REG_FIFO_DATA,bytes([25]));self._wreg(_REG_AUTO_TEST,9);self._wreg(_REG_FIFO_DATA,0);self._wreg(_REG_COMMAND,_CMD_CALC_CRC);sleep_ms(1000);test_output=self.i2c.readfrom_mem(self.addr,_REG_FIFO_DATA,64);version=self.i2c.readfrom_mem(self.addr,_REG_VERSION,1)
	def readID(self):stat,bits=self.request(self.REQIDL);return stat,bits
	def SelectTagSN(self):
		valid_uid=[];status,uid=self.anticoll(self.PICC_ANTICOLL1)
		if status!=self.OK:return self.ERR,[]
		if self.DEBUG:print('anticol(1) {}'.format(uid))
		if self.PcdSelect(uid,self.PICC_ANTICOLL1)==0:return self.ERR,[]
		if self.DEBUG:print('pcdSelect(1) {}'.format(uid))
		if uid[0]==136:
			valid_uid.extend(uid[1:4]);status,uid=self.anticoll(self.PICC_ANTICOLL2)
			if status!=self.OK:return self.ERR,[]
			if self.DEBUG:print('Anticol(2) {}'.format(uid))
			rtn=self.PcdSelect(uid,self.PICC_ANTICOLL2)
			if self.DEBUG:print('pcdSelect(2) return={} uid={}'.format(rtn,uid))
			if rtn==0:return self.ERR,[]
			if self.DEBUG:print('PcdSelect2() {}'.format(uid))
			if uid[0]==136:
				valid_uid.extend(uid[1:4]);status,uid=self.anticoll(self.PICC_ANTICOLL3)
				if status!=self.OK:return self.ERR,[]
				if self.DEBUG:print('Anticol(3) {}'.format(uid))
				if self.MFRC522_PcdSelect(uid,self.PICC_ANTICOLL3)==0:return self.ERR,[]
				if self.DEBUG:print('PcdSelect(3) {}'.format(uid))
		valid_uid.extend(uid[0:5]);return self.OK,valid_uid[:len(valid_uid)-1]
	def anticoll(self,anticolN):
		ser_chk=0;ser=[anticolN,32];self._wreg(13,0);stat,recv,bits=self._tocard(12,ser)
		if stat==self.OK:
			if len(recv)==5:
				for i in range(4):ser_chk=ser_chk^recv[i]
				if ser_chk!=recv[4]:stat=self.ERR
			else:stat=self.ERR
		return stat,recv
	def PcdSelect(self,serNum,anticolN):
		backData=[];buf=[];buf.append(anticolN);buf.append(112)
		for i in serNum:buf.append(i)
		pOut=self._crc(buf);buf.append(pOut[0]);buf.append(pOut[1]);status,backData,backLen=self._tocard(12,buf)
		if status==self.OK and backLen==24:return 1
		else:return 0