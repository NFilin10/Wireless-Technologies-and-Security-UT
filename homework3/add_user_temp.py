#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 3
Name: Nikita Filin
'''

from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString, toASCIIBytes
import hashlib

MIFARE_CLASSIC_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"

cardtype = ATRCardType( toBytes(MIFARE_CLASSIC_ATR) )
cardrequest = CardRequest( timeout=10, cardType=cardtype )
cardservice = cardrequest.waitforcard()

cardservice.connection.connect()


def sendAPDU(APDU):
	data, sw1, sw2 = cardservice.connection.transmit( APDU )

	if [sw1,sw2] == [0x90,0x00]:
		return data
	else:
		print(f'Error sending APDU: {toASCIIString(APDU)}')
		return "Error"


#Getting data from file
f = open("new_employee.txt", "r")

name = f.readline().strip()
first_name = name.split()[0]
last_name = name.split()[1]
print(f'Employee Name: {name}')

department = f.readline().strip()
print(f'Department: {department}')

clearance = f.readline().strip()
print(f'Clearance Level: {clearance}')


#Creating secret code
print("Creating secret...")
apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
uid = sendAPDU(apdu)
uid_formatted = "".join(toHexString(uid).split())
secret = hashlib.sha3_256(name.encode('utf-8') + department.encode('utf-8') + clearance.encode('utf-8')).hexdigest()[:16]


print("Configuring ID card...")
#Data which must to be written
A_keys = ["11 11 11 11 11 11", "22 22  22 22 22 22", "33 33 33 33 33 33", "44 44 44 44 44 44"]
B_key = "FF FF FF FF FF FF"
data = [["EMPLOYEE", first_name, last_name], ["DEPARTMENT", department], ["CLEARANCE", clearance, ''], ["AUTHENTICATION", uid_formatted, secret]]

#writing data in sectors
current_sector = 0
a_key_counter = 0
current_block = 0
i = 4
while i < 20:
	#authentication
	if i % 4 == 0:
		sendAPDU([0xFF, 0x82, 0x00, 0x00, 0x06]+toBytes(B_key))
		sendAPDU([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, i, 0x60, 0x00])
		current_sector += 1
		current_block = 0

	#sector trailer
	if(i%4) == 3:
			sendAPDU([0xFF, 0xD6, 0x00, i, 0x10] + toBytes(A_keys[a_key_counter] + " 78 77 88 41 " + B_key))
			a_key_counter += 1
	
	if i%4 != 3:
		text_length = len(data[current_sector-1][current_block])
		mul_of_16 = 16 - (text_length % 16) if (text_length % 16) != 0 else 0
		text_to_send = toASCIIBytes(data[current_sector-1][current_block]) + toBytes("00"*mul_of_16)

		if i == 9:
			block_nr = 9
			for j in range(0, len(text_to_send), 16):
				sendAPDU([0xFF, 0xD6, 0x00, block_nr, 0x10] + text_to_send[j:j+16])
				block_data = sendAPDU([0xFF, 0xB0, 0x00, block_nr, 0x10])
				block_nr+=1
				i+=1
			if text_length <= 16:
				block_nr+=1
				i+=1
			continue

		else:
			sendAPDU([0xFF, 0xD6, 0x00, i, 0x10] + text_to_send)

	current_block += 1
	i+=1


#creating database entry
db_entry = open(uid_formatted + ".txt", "w")
db_entry.write(secret)
db_entry.close()


print("Creating database entry...")


f.close()
print("Process complete")
