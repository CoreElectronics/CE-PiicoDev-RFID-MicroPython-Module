pet_name = 'Sophie12345678901'
if len(pet_name) > 16:
    pet_name = pet_name[:16]
    print('Pet Name truncated')
pet_name_encoded = pet_name.encode() # returns bytes
pet_name_integer_array = [ord(x) for x in list(pet_name)] # ord() converts to ASCII numbers
print()
print('pet_name')
print(type(pet_name))
print(pet_name)
print()
print('pet_name_encoded')
print(type(pet_name_encoded))
print(pet_name_encoded)
print()
print('pet_name_integer_array')
print(type(pet_name_integer_array))
print(pet_name_integer_array)
