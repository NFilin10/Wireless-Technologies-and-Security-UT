#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 4 template
Reads the ATR of a card, identifies if it has bus card data (ISIC included), 
verifies data on card hasn't been modified, checks if card number in local database
Execution: python3 access_system.py
'''

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString, toASCIIBytes
import hashlib, os

cardtype = AnyCardType()
cardrequest = CardRequest( timeout=10, cardType=cardtype )
cardservice = cardrequest.waitforcard()

cardservice.connection.connect()
#enable line below for Bank ISIC card reading (disconnect then connect to reader after issuing command)
cardservice.connection.transmit([0xFF, 0x00, 0x51, 0xA1, 0x00]) 

#get ATR of current card
current_card_ATR = cardservice.connection.getATR()



#ATR response for Bus cards (to be completed)
TallinBusCard_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"
TartuBusCard_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 3A 00 00 00 00 51"
#This should be the ATR for the bank ISIC cards after the transmit command above is issued 
Swedbank_SEB_ISIC_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 FF 28 00 00 00 00 BC" 


'''
no changes needed here
Hint: You can use something like 
if toASCIIString(send(apdu)) != "Error":
to check if the APDU command failed
'''
def send(apdu):
    data, sw1, sw2 = cardservice.connection.transmit(apdu)

    # success
    if [sw1,sw2] == [0x90,0x00]:
        return data
    else:
        return toASCIIBytes("Error")

'''
converts the the data from the Tallinn/Tartu bus card to ASCII 
This can be useful in searching for pilet.ee
No changes needed here
'''
def prettyHex(content):
	pretty_text = []

	for i in range(len(content)):
		if (content[i] < 33 or content[i] > 126):
			pretty_text.append(46)
		else:
			pretty_text.append(content[i])
			
	return toASCIIString(pretty_text)

#no changes needed here (unless a different data format is required)
def extractTallinnBus():
	card_data = []

	#load athentication key in memory
	send([0xFF, 0x82, 0x00, 0x00, 0x06] + toBytes("d3 f7 d3 f7 d3 f7"))

	for i in range(4,28):
		if(i % 4 == 0):
			#authenticate to the block
			send([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, i, 0x60, 0x00])

		if(i%4 != 3):
			#read every block except sector trailer
			card_data = card_data + send([0xFF, 0xB0, 0x00, i, 0x10])

	return card_data

#no changes needed here (unless a different data format is required)
def extractTartuBus():
	card_data = []


	for i in range(4,40, 4):
		#read every user data page
		card_data = card_data + send([0xFF, 0xB0, 0x00, i, 0x10])

	return card_data


#no changes needed here (unless a different data format is required)
def getBlockInfo(block_nr):
	#load athentication key in memory
	send([0xFF, 0x82, 0x00, 0x00, 0x06] + toBytes("d3 f7 d3 f7 d3 f7"))

	#authenticate to the block
	send([0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block_nr, 0x60, 0x00])

	#get block information
	block_reading = send([0xFF, 0xB0, 0x00, block_nr, 0x10])

	return block_reading


def validBuscard(card_info):
	#TODO
	#This function checks for the pilet.ee string
	if "pilet.ee:ekaart" in prettyHex(card_info):
		return True


def parseNDEF(card_info):
	#TODO
	#extract the nded record from sectors
	if card_info[1] == 255:
		ndef_message_length = int(toHexString(card_info[2:4]).replace(" ", ""), 16)
		ndef_message = card_info[4:4+ndef_message_length]

	else:
		ndef_message_length = card_info[1]
		ndef_message = card_info[2:2+ndef_message_length]

	#get length of data (payload type + payload)
	bus_card_data_length = int(ndef_message[1] + ndef_message[2])
	

	#get data (that has to be signed)
	message = ndef_message[3:3+bus_card_data_length]

	#get the byte containing the signature flags (we need to see if 4 or 1 byte is used for the length)
	sig_flags = ndef_message[bus_card_data_length+3:bus_card_data_length+4]


	
	#the 2nd NDEF record (containing signature and payload type)
	sig_record = ndef_message[bus_card_data_length + 9:]
	

	#check if payload length is 1 or 4 bytes then extract the signature
	if (sig_flags[0]) & int(0x10) == 0:
		sig_length_hex = "".join(toHexString(sig_record[5:7])).replace(" ", "")
		sig_length = int(sig_length_hex, 16)
	
		signature = sig_record[7:128+7]
		sig_end = 13+sig_length
	
	else:
		sig_length_hex = "".join(toHexString(sig_record[2:4])).replace(" ", "")
		sig_length = int(sig_length_hex, 16)
		signature = sig_record[4:4+sig_length]
		sig_end = 4+sig_length


	#check if a certificate is present
	if sig_record[sig_end] == 0:
		cert = ""
	else:
		cert = toASCIIString(sig_record[138:])
	
	

	#the data to be signed, the signature to be decrpyted and the link to the certificate if present
	return message, signature, cert

#Checks if the hashes match
def verifyTallinn(data_hex, signature_hex, cert):
	#calculate data hash
	data_hash = hashlib.sha1(bytes.fromhex(data_hex)).hexdigest()
	der_hash = "3021300906052b0e03021a05000414"+data_hash

	#write der encoded hash or just the hash to a file
	#TODO
	f = open("message_hash.txt", "wb")
	f.write(bytes.fromhex(der_hash))
	f.close()


	#write signature to a file
	#TODO
	f = open("sigdata_file.txt", "wb")
	f.write(bytes.fromhex(signature_hex))
	f.close()

	#grab cert file and store locally
	os.system(f'wget {cert} -q -O certfile.txt')

	#verify hash
	success = os.system(f'openssl pkeyutl -verify -certin -in message_hash.txt -sigfile sigdata_file.txt -inkey certfile.txt')

	
	#success = os.system(f'openssl pkeyutl -verify -certin -in message_hash.txt -sigfile sigdata_file.txt -pkeyopt digest:sha1 -inkey certfile.txt')

	#TODO
	if success == 0:
		return True
	else:
		return False
 
#checks if Tartu bus card is valid
def verifyTartu(data_hex, signature_hex):
	#TODO
	f = open("message_file.txt", "wb")
	f.write(bytes.fromhex(data_hex))
	f.close
	
	f = open("sigdata_file.txt", "wb")
	f.write(bytes.fromhex(signature_hex))
	f.close()

	success = os.system(f'openssl dgst -sha1 -verify ecdsa-live-pub.pem -signature sigdata_file.txt message_file.txt')
	
	if success == 0:
		return True
	else:
		return False

#checks if the card number is on the registered users file
def check_user(card_number):
	#TODO
	f = open("registered_users.txt", "r")
	f = f.read()
	
	
	if card_number in f:
		return True
	else:
		return False

'''
to be completed
0: Runs if a MIFARE Classic card is presented
1: Check if pilett.ee present
2: Get UID from card (GET UID APDU)
3: Get the UID in sector 2
3.1: Check if the card is a 7 byte or 4 byte card so the correct length can be extracted
4: Check if UIDs match
5: Get the data, signature and certificate uri
6: Check if the hash match
7: Get the card number
8: Check if card number is in registered_users.txt file
Bonus: Check if card number is an ISIC card ie starts with 8, extract the card number from Sector 7 and use that to check if user is on the list
'''
def TallinnBusValidator():
	#TODO
	if validBuscard(extractTallinnBus()):
		print('[+] Verifying card...')
		
		apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
		card_uid = send(apdu)
		
		
		data = getBlockInfo(8) + getBlockInfo(9)
		uid_length = data[27:28][0]


		if uid_length == 4:
			data_uid = data[-4:]
		else:
			data_uid = data[-4:] + getBlockInfo(10)[:3]

		if card_uid == data_uid:
			data, signature, cert = parseNDEF(extractTallinnBus())
	

			if verifyTallinn(toHexString(data), toHexString(signature).replace(" ", ""), cert):
				data = getBlockInfo(8) + getBlockInfo(9)
				card_number = data[15:26]
				card_number = toASCIIString(card_number)
					
				if(check_user(card_number)):
					print('[+] Welcome, Player 1')
				else:
					print('[!] Card not registered')

			else:
				print("[!] Invalid card")
		else:
			print("[!] Invalid card")
	else:
		print("[!] Invalid card format")


'''
to be completed
0: Runs if a Ultralight C card is presented
1: Check if pilett.ee present
2: Get UID from card (GET UID APDU)
3: Get the UID in Pages 16 to 19
4: Check if UIDs match
5: Get the data, signature
6: Check if the hash match
7: Get the card number
8: Check if card number is in registered_users.txt file
'''
def TartuBusValidator():
	#TODO
	if validBuscard(extractTartuBus()):
		print('[+] Verifying card...')
		apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
		card_uid = send(apdu)

		data_uid = getBlockInfo(20)[:7]
		if card_uid == data_uid:
			data, signature, cert = parseNDEF(extractTartuBus())

			if verifyTartu(toHexString(data).replace(" ", ""), toHexString(signature).replace(" ", "")):
				card_number = toASCIIString(getBlockInfo(16)[3:14])

				if(check_user(card_number)):
					print('[+] Welcome, Player 1')
				else:
					print('[!] Card not registered')

			else:
				print("[!] Invalid card")
		else:
			print("[!] Invalid card")
	else:
		print("[!] Invalid card format")


#select the type of card to verify
#ATR for your bank ISIC card can be added as well
if current_card_ATR == toBytes(TallinBusCard_ATR):
	TallinnBusValidator()
elif current_card_ATR == toBytes(TartuBusCard_ATR):
	TartuBusValidator()
elif current_card_ATR == toBytes(Swedbank_SEB_ISIC_ATR):
	TallinnBusValidator()
else:
	print("[!] Card type not supported")