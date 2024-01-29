#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 12
Name: Nikita Filin
'''

import zmq
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
import time, os
from datetime import datetime

def TCK_XOR(atr):
	b_list = toBytes(atr)

	TCK = b_list[1]

	for i in range(2,len(b_list)-4):
		TCK = TCK ^ b_list[i]

	b_list.append(TCK)
	return toHexString(b_list)



def sensor():
	cardtype = AnyCardType()
	cardrequest = CardRequest( timeout=None, cardType=cardtype )
	cardservice = cardrequest.waitforcard()
	cardservice.connection.connect()

	print("[+] Card detected")
	#get atr and uid
	atr = toHexString(cardservice.connection.getATR())
	if atr in ATR_list:
		card_type = ATR_list[atr]
	else:
		card_type = "Card Type Unknown"
	uid_apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
	uid, sw1, sw2 = cardservice.connection.transmit(uid_apdu)
	uid = str(toHexString(uid)).replace(' ', '')
	#update log
	update_sensor_log(card_type, uid)

	#return uid
	return uid


def update_sensor_log(card_type, uid):
	print("[+] Updating sensor log")

	now = datetime.now()
	date = now.strftime("%Y/%m/%d")
	
	time_str = now.strftime("%H:%M:%S")

	log_string = f"\t{time_str}\t{card_type} detected: UID {uid}"

	f = open("./logs/nfc_sensor.log", "a+")
	f.seek(0)
	content = f.read()

	if date in content:
		f.write(log_string+"\n")
	else:
		f.write(f"{date}\n")
		f.write(log_string+"\n")

	f.close()



#add your favourite ATRs here
ATR_list = {
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00"): "MIFARE Classic 1K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 02 00 00 00 00"): "MIFARE Classic 4K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00"): "MIFARE Ultralight",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 26 00 00 00 00"): "MIFARE Mini",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 3A 00 00 00 00"): "MIFARE Ultralight C",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 36 00 00 00 00"): "MIFARE Plus SL1 2K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 37 00 00 00 00"): "MIFARE Plus SL1 4K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 38 00 00 00 00"): "MIFARE Plus SL2 2K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 39 00 00 00 00"): "MIFARE Plus SL2 4K",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 30 00 00 00 00"): "Topaz and Jewel",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 11 00 3B 00 00 00 00"): "FeliCa",
	TCK_XOR("3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 FF 28 00 00 00 00"): "JCOP 30",
	"3B 81 80 01 80 80": "MIFARE DESFire",
	"3B 88 80 01 1C 2D 94 11 F7 71 85 00 BE":"EZ-Link",
	"3B 86 80 01 06 75 77 81 02 80 00":"DESFire",
	"3B 8C 80 01 50 12 23 45 56 12 53 54 4E 33 81 C3 55":"ST19XRC8E",
}

#configure sockets
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

while True:
	#get UID from card
	uid = sensor()

	#send UID to processor
	socket.send(uid.encode())

	time.sleep(10)
