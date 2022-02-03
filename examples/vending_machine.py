#ToDo write a function to detect card removal

from PiicoDev_RFID import *

cost = 95 # Always use ints when dealing with currency (cents)

rfid = PiicoDev_RFID()

print('Place tag near the PiicoDev RFID Module to purchase for ', end='')
cost_formatted = '${:,.2f}'.format(cost/100)
print(cost_formatted)
print('')

# Give credit
topup = False
if topup:
    rfid.writeNumberToTag(10000) #cents
    break_here

while True:
    balance_previous = rfid.readNumberFromTag()
    balance_previous_formatted = '${:,.2f}'.format(balance_previous/100)
    print('Previous Balance: ', end=''); print(balance_previous_formatted)
    
    new_balance = balance_previous - cost
    
    if new_balance < 0:
        print('Not enough credit')
    
    if new_balance >= 0:
        print('Item dispensed')
        success = rfid.writeNumberToTag(new_balance)
        
        new_balance = rfid.readNumberFromTag()
        new_balance_formatted = '${:,.2f}'.format(new_balance/100)
        print('New Balance: ', end=''); print(new_balance_formatted)
        
        # Wait for the user to remove the tag
        read_tag_id_result = rfid.readTagID()
        while read_tag_id_result['success']:
            read_tag_id_result = rfid.readTagID()

    sleep_ms(2000)
    print('')
    print('Place tag near the PiicoDev RFID Module to purchase for ', end='')
    cost_formatted = '${:,.2f}'.format(cost/100)
    print(cost_formatted)
