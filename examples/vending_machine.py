from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID()   # Initialise the RFID module

price = 3 # dollars (whole dollars only)

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module to purchase for $' + str(price))
print('')

rfid.writeNumber(100) # Give credit (whole dollars only)

while True:
    balance_dollars = rfid.readNumber()
    print('Previous Balance: $' + str(balance_dollars))
    
    new_balance = balance_dollars - price
    
    if new_balance < 0:
        print('Not enough credit')
    
    if new_balance >= 0:
        print('Item dispensed')
        success = rfid.writeNumber(new_balance)
        
        new_balance = rfid.readNumber()
        print('New Balance: $' + str(new_balance))
        
        # Wait for the user to remove the tag
        while rfid.tagPresent():
            sleep_ms(10)

    sleep_ms(2000)
    print('')
    print('Place tag near the PiicoDev RFID Module to purchase for $' + str(price))
