#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 3
Name: Nikita Filin
'''

from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString, toASCIIBytes
from random import randrange
import sys, os, hashlib

MIFARE_CLASSIC_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"

cardtype = ATRCardType( toBytes(MIFARE_CLASSIC_ATR) )
cardrequest = CardRequest( timeout=5, cardType=cardtype )
cardservice = cardrequest.waitforcard()

cardservice.connection.connect()


def sendAPDU(APDU):
	data, sw1, sw2 = cardservice.connection.transmit( APDU )

	if [sw1,sw2] == [0x90,0x00]:
		return data
	else:
		print(f'Error sending APDU: {APDU}')
		return "Error"
	


door_level = randrange(6)
print(f'Door Entry Level: {door_level}')


A_keys = ["11 11 11 11 11 11", "22 22  22 22 22 22", "33 33 33 33 33 33", "44 44 44 44 44 44"]
B_key = "FF FF FF FF FF FF"


def read_block(block_nr):

		sendAPDU([0xFF, 0x82, 0x00, 0x00, 0x06]+toBytes(A_keys[block_nr//4-1]))
		sendAPDU([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block_nr, 0x60, 0x00])
		block_data = sendAPDU([0xFF, 0xB0, 0x00, block_nr, 16])
		return(toASCIIString(block_data))			


apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
card_uid = sendAPDU(apdu)
card_uid_formatted = "".join(toHexString(card_uid).split())

card_uid_block = read_block(17).replace(".", "")

if card_uid_formatted == card_uid_block:

	if os.path.isfile(card_uid_block+".txt"):
		name = (read_block(5).replace(".", "") + " " + read_block(6).replace(".", "")).strip()
		department = (read_block(9).replace(".", "") + read_block(10).replace(".", "")).strip()
		clearance = (read_block(13).replace(".", "")).strip()
		secret = hashlib.sha3_256(name.encode('utf-8') + department.encode('utf-8') + clearance.encode('utf-8')).hexdigest()[:16]
		if secret == open(card_uid_block+".txt").readline():
			if int(clearance) >= door_level:
				print(f'Employee: {name}')
				print(f'Department: {department}')
				print(f'You are cleared for entry!')
			else:
				sys.exit("Access Denied! No clearance")
		else:
			sys.exit("Access Denied! Verification failed")
	else:
		sys.exit("Access Denied! Card not in database")	

else:
	sys.exit("Access Denied! Invalid card format")


