#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Lab 4
Copy the NDEF records from the SEB ISIC card shown in Lecture 4 to a Classic fob
Execution: python3 copy_sample_SEB_ISIC.py
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
	#sendAPDU([0xFF, 0xD6, 0x00, 0, 16] + toBytes("05 8B A9 01 EA A1 00 28 44 00 F9 00 00 00 00 40"))
	sendAPDU([0xFF, 0xD6, 0x00, 1, 16] + toBytes("B0 00 03 E1 03 E1 03 E1 03 E1 03 E1 03 E1 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 3, 16] + toBytes("A0 A1 A2 A3 A4 A5 79 67 88 C1 FF FF FF FF FF FF"))


#Sector 1
can_write = auth_block(4)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 4, 16] + toBytes("03 FF 01 04 94 11 3B 70 69 6C 65 74 2E 65 65 3A"))
	sendAPDU([0xFF, 0xD6, 0x00, 5, 16] + toBytes("65 6B 61 61 72 74 3A 32 66 19 5F 26 06 32 30 31"))
	sendAPDU([0xFF, 0xD6, 0x00, 6, 16] + toBytes("31 30 31 59 04 32 31 31 32 5F 28 03 32 33 33 5F"))
	sendAPDU([0xFF, 0xD6, 0x00, 7, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))


#Sector 2
can_write = auth_block(8)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 8, 16] + toBytes("27 01 31 6E 1E 5A 13 39 32 33 33 37 33 36 35 38"))
	sendAPDU([0xFF, 0xD6, 0x00, 9, 16] + toBytes("30 31 36 32 38 36 36 35 30 33 53 07 05 8B A9 01"))
	sendAPDU([0xFF, 0xD6, 0x00, 10, 16] + toBytes("EA A1 00 41 03 00 00 00 AC 53 69 67 01 02 00 80"))
	sendAPDU([0xFF, 0xD6, 0x00, 11, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))

#Sector 3
can_write = auth_block(12)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 12, 16] + toBytes("A0 2D AA 05 28 BD 4C 03 73 43 2F 45 E2 C0 54 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 13, 16] + toBytes("D7 01 16 DC 16 92 2C E8 34 6A 21 92 A6 EB 18 6E"))
	sendAPDU([0xFF, 0xD6, 0x00, 14, 16] + toBytes("24 1E BC CE 42 65 55 0A F2 95 C0 63 69 EC 4C A8"))
	sendAPDU([0xFF, 0xD6, 0x00, 15, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))

#Sector 4
can_write = auth_block(16)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 16, 16] + toBytes("E0 2D C4 F9 BF FC 08 12 D7 7D DA FD 2B EA 65 18"))
	sendAPDU([0xFF, 0xD6, 0x00, 17, 16] + toBytes("B5 55 44 DA 67 FB 21 E4 B6 FE C9 97 82 F0 EB 8D"))
	sendAPDU([0xFF, 0xD6, 0x00, 18, 16] + toBytes("29 0A C4 68 E3 BF A4 4F AD 94 F4 75 82 60 27 4E"))
	sendAPDU([0xFF, 0xD6, 0x00, 19, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))

#Sector 5
can_write = auth_block(20)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 20, 16] + toBytes("78 66 69 21 28 F9 BA DA 0D 80 B3 2C C1 1D E0 52"))
	sendAPDU([0xFF, 0xD6, 0x00, 21, 16] + toBytes("E1 EC 28 D9 9F 31 BC D7 7F 9D FD AC DB 95 E5 2D"))
	sendAPDU([0xFF, 0xD6, 0x00, 22, 16] + toBytes("80 00 25 68 74 74 70 3A 2F 2F 70 69 6C 65 74 2E"))
	sendAPDU([0xFF, 0xD6, 0x00, 23, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))

#Sector 6
can_write = auth_block(24)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 24, 16] + toBytes("65 65 2F 63 72 74 2F 39 32 33 33 37 33 36 35 2D"))
	sendAPDU([0xFF, 0xD6, 0x00, 25, 16] + toBytes("30 30 30 31 2E 63 72 74 FE 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 26, 16] + toBytes("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 27, 16] + toBytes("D3 F7 D3 F7 D3 F7 7F 07 88 40 FF FF FF FF FF FF"))


#ISIC Specific Sectors
#Sector 7

#Sector 8

#Sector 9

#Sector 10

