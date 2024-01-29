#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Lab 4
Copy the NDEF records from the School ISIC card shown in Lecture 4 to a Classic fob
Execution: python3 copy_sample_ISIC7.py
'''


from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString

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
		return f'Error sending APDU: {toHexString(APDU)}'


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
	#sendAPDU([0xFF, 0xD6, 0x00, 0, 16] + toBytes("04 77 D2 BA 15 3C 80 88 44 00 C8 20 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 1, 16] + toBytes("B0 00 03 E1 03 E1 03 E1 03 E1 03 E1 03 E1 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 3, 16] + toBytes("A0 A1 A2 A3 A4 A5 0F 07 8F C1 FF FF FF FF FF FF"))


#Sector 1
can_write = auth_block(4)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 4, 16] + toBytes("03 FF 01 04 94 11 3B 70 69 6C 65 74 2E 65 65 3A"))
	sendAPDU([0xFF, 0xD6, 0x00, 5, 16] + toBytes("65 6B 61 61 72 74 3A 32 66 19 5F 26 06 31 37 30"))
	sendAPDU([0xFF, 0xD6, 0x00, 6, 16] + toBytes("32 30 39 59 04 31 37 31 32 5F 28 03 32 33 33 5F"))
	sendAPDU([0xFF, 0xD6, 0x00, 7, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))


#Sector 2
can_write = auth_block(8)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 8, 16] + toBytes("27 01 31 6E 1E 5A 13 39 32 33 33 37 33 31 36 38"))
	sendAPDU([0xFF, 0xD6, 0x00, 9, 16] + toBytes("30 31 32 30 33 31 35 38 37 37 53 07 04 77 D2 BA"))
	sendAPDU([0xFF, 0xD6, 0x00, 10, 16] + toBytes("15 3C 80 41 03 00 00 00 AC 53 69 67 01 02 00 80"))
	sendAPDU([0xFF, 0xD6, 0x00, 11, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 3
can_write = auth_block(12)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 12, 16] + toBytes("40 C0 52 FC BC 9C F4 2D 82 D1 E9 81 B5 39 EA A8"))
	sendAPDU([0xFF, 0xD6, 0x00, 13, 16] + toBytes("6F F0 29 83 9F BC 2E A6 30 33 A5 6B 5D 88 65 42"))
	sendAPDU([0xFF, 0xD6, 0x00, 14, 16] + toBytes("BB 8F F5 CF 07 AE 52 8E FD 0C 37 CA B0 92 6C D8"))
	sendAPDU([0xFF, 0xD6, 0x00, 15, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 4
can_write = auth_block(16)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 16, 16] + toBytes("B8 22 76 9D 64 30 2E 3A F8 71 32 59 90 EF B0 3B"))
	sendAPDU([0xFF, 0xD6, 0x00, 17, 16] + toBytes("36 B8 A7 2C 70 A7 19 94 EF 5C 84 6F 1F FB 32 1D"))
	sendAPDU([0xFF, 0xD6, 0x00, 18, 16] + toBytes("B6 02 26 E0 8D FF 04 C6 A1 6F E7 F3 9B 0E ED 86"))
	sendAPDU([0xFF, 0xD6, 0x00, 19, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 5
can_write = auth_block(20)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 20, 16] + toBytes("F2 B8 A7 ED 5C 6E 2D 4C A9 01 E0 77 1E 86 BA 5D"))
	sendAPDU([0xFF, 0xD6, 0x00, 21, 16] + toBytes("FD C0 95 61 5E 62 0B 23 82 97 0F 9B 02 70 C6 6A"))
	sendAPDU([0xFF, 0xD6, 0x00, 22, 16] + toBytes("80 00 25 68 74 74 70 3A 2F 2F 70 69 6C 65 74 2E"))
	sendAPDU([0xFF, 0xD6, 0x00, 23, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 6
can_write = auth_block(24)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 24, 16] + toBytes("65 65 2F 63 72 74 2F 39 32 33 33 37 33 31 36 2D"))
	sendAPDU([0xFF, 0xD6, 0x00, 25, 16] + toBytes("30 30 30 31 2E 63 72 74 FE 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 26, 16] + toBytes("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 27, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))


#ISIC Specific Sectors
#Sector 7

#Sector 8

#Sector 9

#Sector 10