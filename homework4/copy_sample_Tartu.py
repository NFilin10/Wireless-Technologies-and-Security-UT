#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Lab 4
Copy the NDEF records from the Tartu Bus shown in Lecture 4 to a Ultralight C fob
Execution: python3 copy_sample_Tartu.py
'''


from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString

MIFARE_CLASSIC_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"
MIFARE_ULTRA_C_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 3A 00 00 00 00 51"

cardtype = ATRCardType( toBytes(MIFARE_ULTRA_C_ATR) )
cardrequest = CardRequest( timeout=5, cardType=cardtype )
cardservice = cardrequest.waitforcard()

cardservice.connection.connect()


def sendAPDU(APDU):
	data, sw1, sw2 = cardservice.connection.transmit( APDU )

	if [sw1,sw2] == [0x90,0x00]:
		return data
	else:
		#return f'Error sending APDU: {toHexString(APDU)}'
		print(f'Error {hex(sw1)} {hex(sw2)} sending APDU: {toHexString(APDU)}')



#configure Ultralight C as NDEF card
#sendAPDU([0xFF, 0xD6, 0x00, 3, 4] + toBytes("e1 10 12 00"))

#write the bus card values onto the data pages
sendAPDU([0xFF, 0xD6, 0x00, 4, 16] + toBytes("03 8B 94 11  35 70 69 6C  65 74 2E 65  65 3A 65 6B"))
sendAPDU([0xFF, 0xD6, 0x00, 8, 16] + toBytes("61 61 72 74  3A 33 66 0F  5F 26 06 31  35 30 38 33"))
sendAPDU([0xFF, 0xD6, 0x00, 12, 16] + toBytes("31 59 04 20  20 20 20 6E  22 5A 13 33  30 38 36 34"))		
sendAPDU([0xFF, 0xD6, 0x00, 16, 16] + toBytes("39 30 30 39  39 35 30 30  33 38 32 32  38 33 53 07"))
sendAPDU([0xFF, 0xD6, 0x00, 20, 16] + toBytes("04 97 34 C2  83 3F 80 54  02 00 01 51  03 3C 53 69"))
sendAPDU([0xFF, 0xD6, 0x00, 24, 16] + toBytes("67 01 04 00  37 30 35 02  19 00 82 76  C7 18 46 5D"))
sendAPDU([0xFF, 0xD6, 0x00, 28, 16] + toBytes("5C B4 CC 9C  4F 84 BB 97  A8 FC BB CE  AB 6D E1 7F"))
sendAPDU([0xFF, 0xD6, 0x00, 32, 16] + toBytes("CB 16 02 18  1D A6 92 C7  70 BB D4 CB  53 3D 82 D7"))
sendAPDU([0xFF, 0xD6, 0x00, 36, 16] + toBytes("4F 81 F5 06  09 C6 BC 56  CD 9F 96 05  00 00 00 00"))

