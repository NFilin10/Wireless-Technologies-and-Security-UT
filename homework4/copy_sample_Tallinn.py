#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Lab 4
Copy the NDEF records from the Tallinn Bus card shown in Lecture 4 to a Classic fob
Execution: python3 copy_sample_Tallinn.py
'''


from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString
import time

MIFARE_CLASSIC_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"
MIFARE_ULTRA_C_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 3A 00 00 00 00 51"

cardtype = ATRCardType( toBytes(MIFARE_CLASSIC_ATR) )
cardrequest = CardRequest( timeout=5, cardType=cardtype )
cardservice = cardrequest.waitforcard()

cardservice.connection.connect()


def sendAPDU(APDU):
	data, sw1, sw2 = cardservice.connection.transmit( APDU )

	if [sw1,sw2] == [0x90,0x00]:
		return data
	else:
		print(f'Error {hex(sw1)}{hex(sw2)}')
		return 'Error'


def auth_block(block_nbr):
	#try authenticating with key A
	auth = sendAPDU([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block_nbr, 0x60, 0x00])

	#try auth with key B
	if auth == 'Error':
		auth = sendAPDU([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block_nbr, 0x61, 0x00])	

	if auth == 'Error':
		print(f"Unable to authenticate Sector {int(block_nbr/4)}")
		return False
	else:
		return True




#Assumes the current A and B keys are FF FF FF FF FF FF
#run the reset_card.py script first if the default keys are not currently set

#load key in memory 0x00
sendAPDU([0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

#NDEF Sector Configuration
can_write = auth_block(0)

if can_write:
	#sendAPDU([0xFF, 0xD6, 0x00, 0, 16] + toBytes("10 9c 54 33 eb 08 04 00 62 63 64 65 66 67 68 69"))
	sendAPDU([0xFF, 0xD6, 0x00, 1, 16] + toBytes("b0 00 03 e1 03 e1 03 e1 03 e1 03 e1 03 e1 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 3, 16] + toBytes("A0 A1 A2 A3 A4 A5 0F 07 8F C1 FF FF FF FF FF FF"))


#Sector 1
can_write = auth_block(4)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 4, 16] + toBytes("03 ff 01 01 94 11 38 70 69 6c 65 74 2e 65 65 3a"))
	sendAPDU([0xFF, 0xD6, 0x00, 5, 16] + toBytes("65 6b 61 61 72 74 3a 32 66 19 5f 26 06 31 34 31"))
	sendAPDU([0xFF, 0xD6, 0x00, 6, 16] + toBytes("30 32 30 59 04 20 20 20 20 5f 28 03 32 33 33 5f"))
	sendAPDU([0xFF, 0xD6, 0x00, 7, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))


#Sector 2
can_write = auth_block(8)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 8, 16] + toBytes("27 01 31 6e 1b 5a 13 33 30 38 36 34 39 30 30 39"))
	sendAPDU([0xFF, 0xD6, 0x00, 9, 16] + toBytes("30 30 30 37 35 39 39 37 31 39 53 04 10 9c 54 33"))
	sendAPDU([0xFF, 0xD6, 0x00, 10, 16] + toBytes("41 03 00 00 00 ac 53 69 67 01 02 00 80 a1 22 8f"))
	sendAPDU([0xFF, 0xD6, 0x00, 11, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 3
can_write = auth_block(12)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 12, 16] + toBytes("cf ff 67 82 ad cc 6a 11 17 97 f1 84 30 84 38 a9"))
	sendAPDU([0xFF, 0xD6, 0x00, 13, 16] + toBytes("af 3a c9 bf d9 08 cd 20 27 2d 95 64 52 1e 57 e5"))
	sendAPDU([0xFF, 0xD6, 0x00, 14, 16] + toBytes("86 22 16 3b f0 2e 91 9b 59 13 bb e7 b2 56 c4 cf"))
	sendAPDU([0xFF, 0xD6, 0x00, 15, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 4
can_write = auth_block(16)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 16, 16] + toBytes("b4 c6 1a c2 cf 8f c9 5d d5 c3 df cb e7 3b fb 08"))
	sendAPDU([0xFF, 0xD6, 0x00, 17, 16] + toBytes("3a a6 74 d6 c1 32 33 ba 4e af b9 08 7a 33 f3 92"))
	sendAPDU([0xFF, 0xD6, 0x00, 18, 16] + toBytes("8b 5b c4 85 6c 41 13 e2 2c 09 99 0d f1 53 e3 c2"))
	sendAPDU([0xFF, 0xD6, 0x00, 19, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 5
can_write = auth_block(20)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 20, 16] + toBytes("bb 55 7c 06 23 3c e6 71 1b 7f eb 2a 88 1c 39 02"))
	sendAPDU([0xFF, 0xD6, 0x00, 21, 16] + toBytes("5e 78 b6 fc a9 66 72 ba 51 1b ca 98 40 80 00 25"))
	sendAPDU([0xFF, 0xD6, 0x00, 22, 16] + toBytes("68 74 74 70 3a 2f 2f 70 69 6c 65 74 2e 65 65 2f"))
	sendAPDU([0xFF, 0xD6, 0x00, 23, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 6
can_write = auth_block(24)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 24, 16] + toBytes("63 72 74 2f 33 30 38 36 34 39 30 30 2d 30 30 30"))
	sendAPDU([0xFF, 0xD6, 0x00, 25, 16] + toBytes("31 2e 63 72 74 fe 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 26, 16] + toBytes("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 27, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

