_A=None
from PiicoDev_Unified import *
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
_I2C_ADDRESS=44
_REG_COMMAND=1
_REG_COM_I_EN=2
_REG_STATUS_1=7
_REG_STATUS_2=8
_REG_FIFO_DATA=9
_REG_MODE=17
_REG_TX_ASK=21
_REG_BIT_FRAMING=13
_REG_T_MODE=42
_REG_T_PRESCALER=43
_REG_T_RELOAD_HI=44
_REG_T_RELOAD_LO=45
_REG_AUTO_TEST=54
_REG_VERSION=55
_CMD_CALC_CRC=3
_CMD_SOFT_RESET=15
def _writeNibble(x,n,c):x=_writeBit(x,n,_readBit(c,0));return _writeBit(x,n+1,_readBit(c,1))
class PiicoDev_MFRC522:
	OK=0;NOTAGERR=1;ERR=2;REQIDL=38;REQALL=82;AUTHENT1A=96;AUTHENT1B=97
	def __init__(self,bus=_A,freq=_A,sda=_A,scl=_A,addr=_I2C_ADDRESS):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl);self.addr=addr;self.init()
	def _wreg(self,reg,val):self.i2c.writeto_mem(self.addr,reg,bytes(val))
	def _rreg(self,reg):val=self.i2c.readfrom_mem(self.addr,reg,1);return val[0]
	def _sflags(self,reg,mask):self._wreg(reg,self._rreg(reg)|mask)
	def _cflags(self,reg,mask):self._wreg(reg,self._rreg(reg)&~ mask)
	def _tocard(self,cmd,send):
		recv=[];bits=irq_en=wait_irq=n=0;stat=self.ERR
		if cmd==14:irq_en=18;wait_irq=16
		elif cmd==12:irq_en=119;wait_irq=48
		self._wreg(_REG_COM_I_EN,irq_en|128);self._cflags(4,128);self._sflags(10,128);self._wreg(_REG_COMMAND,0)
		for c in send:self._wreg(9,c)
		self._wreg(1,cmd)
		if cmd==12:self._sflags(_REG_BIT_FRAMING,128)
		i=2000
		while True:
			n=self._rreg(4);i-=1
			if~(i!=0 and~(n&1)and~(n&wait_irq)):break
		self._cflags(_REG_BIT_FRAMING,128)
		if i:
			if self._rreg(6)&27==0:
				stat=self.OK
				if n&irq_en&1:stat=self.NOTAGERR
				elif cmd==12:
					n=self._rreg(10);lbits=self._rreg(12)&7
					if lbits!=0:bits=(n-1)*8+lbits
					else:bits=n*8
					if n==0:n=1
					elif n>16:n=16
					for _ in range(n):recv.append(self._rreg(9))
			else:stat=self.ERR
		return stat,recv,bits
	def _crc(self,data):
		self._cflags(5,4);self._sflags(10,128)
		for c in data:self._wreg(9,c)
		self._wreg(1,3);i=255
		while True:
			n=self._rreg(5);i-=1
			if not(i!=0 and not n&4):break
		return[self._rreg(34),self._rreg(33)]
	def init(self):self.reset();self._wreg(_REG_T_MODE,128);self._wreg(_REG_T_PRESCALER,169);self._wreg(_REG_T_RELOAD_HI,3);self._wreg(_REG_T_RELOAD_LO,232);self._wreg(_REG_TX_ASK,64);self._wreg(_REG_MODE,61);self.antenna_on();print('device initialised')
	def reset(self):self._wreg(_REG_COMMAND,_CMD_SOFT_RESET)
	def antenna_on(self,on=True):
		if on and~(self._rreg(20)&3):self._sflags(20,3)
		else:self._cflags(20,3)
	def request(self,mode):
		print('Request Made');self._wreg(_REG_BIT_FRAMING,7);stat,recv,bits=self._tocard(12,[mode]);print(stat);print(recv);print(bits)
		if(stat!=self.OK)|(bits!=16):stat=self.ERR
		return stat,bits
	def anticoll(self):
		ser_chk=0;ser=[147,32];self._wreg(_REG_BIT_FRAMING,0);stat,recv,bits=self._tocard(12,ser)
		if stat==self.OK:
			if len(recv)==5:
				for i in range(4):ser_chk=ser_chk^recv[i]
				if ser_chk!=recv[4]:stat=self.ERR
			else:stat=self.ERR
		return stat,recv
	def select_tag(self,ser):buf=[147,112]+ser[:5];buf+=self._crc(buf);stat,recv,bits=self._tocard(12,buf);return self.OK if stat==self.OK and bits==24 else self.ERR
	def auth(self,mode,addr,sect,ser):return self._tocard(14,[mode,addr]+sect+ser[:4])[0]
	def stop_crypto1(self):self._cflags(_REG_STATUS_2,8);print('crypto off')
	def read(self,addr):data=[48,addr];data+=self._crc(data);stat,recv,_=self._tocard(12,data);return recv if stat==self.OK else _A
	def write(self,addr,data):
		buf=[160,addr];buf+=self._crc(buf);stat,recv,bits=self._tocard(12,buf)
		if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		else:
			buf=[]
			for i in range(16):buf.append(data[i])
			buf+=self._crc(buf);stat,recv,bits=self._tocard(12,buf)
			if not stat==self.OK or not bits==4 or not recv[0]&15==10:stat=self.ERR
		return stat
	def SelfTest(self):self.reset();self._wreg(_REG_FIFO_DATA,bytearray(25));self._wreg(_REG_AUTO_TEST,9);self._wreg(_REG_FIFO_DATA,0);self._wreg(_REG_COMMAND,_CMD_CALC_CRC);sleep_ms(1000);test_output=self.i2c.readfrom_mem(self.addr,_REG_FIFO_DATA,64);print('test output');print(test_output);version=self.i2c.readfrom_mem(self.addr,_REG_VERSION,1);print('version');print(version)