from PiicoDev_RFID import *

rfid = PiicoDev_RFID()
register = 8

print('Place tag near the PiicoDev RFID Module')
print('')

while True:
    text = rfid.readTextFromTag()
    print('Text in tag ', end=''); print(register, end=''); print(': ', end=''); print(tag_text)
    print()
    sleep_ms(1000)
