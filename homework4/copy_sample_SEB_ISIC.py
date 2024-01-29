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
	#sendAPDU([0xFF, 0xD6, 0x00, 0, 16] + toBytes("4B F2 AC F8 ED 88 04 00 C0 8E 3E 95 49 20 32 14"))
	sendAPDU([0xFF, 0xD6, 0x00, 1, 16] + toBytes("B0 00 03 E1 03 E1 03 E1 03 E1 03 E1 03 E1 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 3, 16] + toBytes("A0 A1 A2 A3 A4 A5 0F 07 8F C1 FF FF FF FF FF FF"))


#Sector 1
can_write = auth_block(4)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 4, 16] + toBytes("03 FF 01 01 94 11 38 70 69 6C 65 74 2E 65 65 3A"))
	sendAPDU([0xFF, 0xD6, 0x00, 5, 16] + toBytes("65 6B 61 61 72 74 3A 32 66 19 5F 26 06 31 35 30"))
	sendAPDU([0xFF, 0xD6, 0x00, 6, 16] + toBytes("39 30 38 59 04 31 36 31 32 5F 28 03 32 33 33 5F"))
	sendAPDU([0xFF, 0xD6, 0x00, 7, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))


#Sector 2
can_write = auth_block(8)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 8, 16] + toBytes("27 01 31 6E 1B 5A 13 39 32 33 33 37 33 33 31 38"))
	sendAPDU([0xFF, 0xD6, 0x00, 9, 16] + toBytes("30 31 34 30 35 30 30 35 30 37 53 04 4B F2 AC F8"))
	sendAPDU([0xFF, 0xD6, 0x00, 10, 16] + toBytes("41 03 00 00 00 AC 53 69 67 01 02 00 80 59 AF 3D"))
	sendAPDU([0xFF, 0xD6, 0x00, 11, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 3
can_write = auth_block(12)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 12, 16] + toBytes("D2 15 AF 11 D2 FD 6F 6D F2 5E 25 5E 94 C0 24 CB"))
	sendAPDU([0xFF, 0xD6, 0x00, 13, 16] + toBytes("8F 18 ED 94 2A 59 29 C7 36 71 49 2C B3 95 D8 9C"))
	sendAPDU([0xFF, 0xD6, 0x00, 14, 16] + toBytes("9D A6 62 6A 6E D2 89 CB 7E 04 13 5B F2 15 1C B7"))
	sendAPDU([0xFF, 0xD6, 0x00, 15, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 4
can_write = auth_block(16)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 16, 16] + toBytes("81 34 B4 DE 39 DF 07 93 81 0D 98 C2 56 D1 C3 9E"))
	sendAPDU([0xFF, 0xD6, 0x00, 17, 16] + toBytes("B3 EB 3A 75 19 FD 76 E0 15 95 89 68 92 AE 7E A7"))
	sendAPDU([0xFF, 0xD6, 0x00, 18, 16] + toBytes("52 6E FD 2A 84 C1 D2 56 AD 20 17 15 73 0C 5F 64"))
	sendAPDU([0xFF, 0xD6, 0x00, 19, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 5
can_write = auth_block(20)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 20, 16] + toBytes("3C 89 6B 7E 16 B8 6E E0 37 08 DE BD FA 96 D1 97"))
	sendAPDU([0xFF, 0xD6, 0x00, 21, 16] + toBytes("4E D7 11 11 A4 B7 EF FA 3A 41 93 99 8D 80 00 25"))
	sendAPDU([0xFF, 0xD6, 0x00, 22, 16] + toBytes("68 74 74 70 3A 2F 2F 70 69 6C 65 74 2E 65 65 2F"))
	sendAPDU([0xFF, 0xD6, 0x00, 23, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))

#Sector 6
can_write = auth_block(24)

if can_write:
	sendAPDU([0xFF, 0xD6, 0x00, 24, 16] + toBytes("63 72 74 2F 39 32 33 33 37 33 33 31 2D 30 30 30"))
	sendAPDU([0xFF, 0xD6, 0x00, 25, 16] + toBytes("32 2E 63 72 74 FE 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 26, 16] + toBytes("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
	sendAPDU([0xFF, 0xD6, 0x00, 27, 16] + toBytes("D3 F7 D3 F7 D3 F7 0F 07 8F 41 FF FF FF FF FF FF"))


#ISIC Specific Sectors
#Sector 7

#Sector 8

#Sector 9

#Sector 10