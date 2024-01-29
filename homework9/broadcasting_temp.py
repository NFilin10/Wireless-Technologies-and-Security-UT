#!/usr/bin/env python3

'''
https://docs.python.org/3/library/secrets.html
$python3 -m pip install pycryptodome or pip3 install pycryptodome

Generates a random ID, random MAC address and encrypted metadata and sends out exposure notifications

Wireless Technologies and Security (LTAT.04.009) Homework 9 template
Executing Script: 
'''
from Crypto.Cipher import AES 
from Crypto.Util import Counter
import sys, os, time, datetime, hashlib, secrets
from random import randrange


def generate_temp_exp_key():
	#get a random 16 byte number to represent the Temporary Exposure Key
	return secrets.token_bytes(16)


def generate_random_id(exp_key):
	#create a rolling proximity key
	random_identifier_key = hashlib.pbkdf2_hmac('sha256', exp_key, b"EN-RPIK", 4096, 16)

	#create the rolling proximity data
	ENIN = int(time.time() / 600) + randrange(500) #enable to add some randomness so the random id updates for the 1 minute testing
	random_data = b"EN-RPI" + b'\x00\x00\x00\x00\x00\x00' + ENIN.to_bytes(4, byteorder='little')#this should be 16 bytes

	#rolling code is made by encrypting data with rolling proximity key
	cipher = AES.new(random_identifier_key, AES.MODE_CTR)
	random_identifier = cipher.encrypt(random_data)

	return random_identifier.hex()

def generate_metadata(exp_key, random_id):
	#create a metadata key
	metadata_key = hashlib.pbkdf2_hmac('sha256', exp_key, b"EN-AEMK", 4096, 16)

	#medata: byte 0: versioning, byte 2: transmit power, byte and 3 reserved
	metadata = b'\x40\x3B\x00\x00'

	#metadata is encrypted with metadata key with random id as an IV
	cipher = AES.new(metadata_key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int(random_id, 16)))
	encrypted_metadata = cipher.encrypt(metadata)

	return encrypted_metadata.hex()

def check_install():
	btle_install_location = "/usr/src/BTLE" #DragonOS install location of BTLE
	#btle_install_location = "/home/.../BTLE" #personal install location of BTLE

	#if os.path.exists(f"{btle_install_location}/host/build/btle-tools/src"):
	if os.path.exists(f"{btle_install_location}"):
		os.chdir(f"{btle_install_location}")
		#os.chdir(f"{btle_install_location}/host/build/btle-tools/src")
		return True
	else:
		return False


def update_generated_file(temp_key, document_location):
	#write the random id to the file
	
	current_date = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")


	f = open(f"{document_location}/generated_keys.txt", "a")
	f.write(f'{temp_key.hex()}\t{current_date}\n')
	f.close()
		

def transmit_beacon(random_id, mac_address, metadata):
	#print(f"[+] Transmitting exposure information...")

	channels = [37, 38, 39]

	for channel in channels:
		# Transmit a packet on the current channel
		command = f'./btle_tx {channel}-ADV_NONCONN_IND-TxAdd-1-RxAdd-0-AdvA-{mac_address}-AdvData-02011A03036ffd17166ffd{random_id}{metadata}-Space-10 r20'
		os.popen(command)

	
	
def broadcast(working_location):
	print(f"Welcome to the Exposure Notification App")
	user_choice = input("[?] Do you consent to the use of this app: ")

	if user_choice.lower() == 'y':
		if check_install():
			#create Temporary #create Temporary Exposure Key and create timerKey and create timer
			TEKey = generate_temp_exp_key()

			print(f"[+] Today's Temporary Key: {TEKey.hex()}")

			#save random id to file
			update_generated_file(TEKey, working_location+'/database_files')

			'''
			create privacy data: rolling code, random MAC address, changing metadata
			'''
			#create random id and create timer
			random_id = generate_random_id(TEKey)

			#generate metadata
			meta = generate_metadata(TEKey, random_id)

			#create random mac address
			mac_address = secrets.token_hex(6)

			print(f"[+] Exposure data\n\tid: {random_id}\n\tMAC address: {mac_address}\n\tMetadata: {meta}")

			start1 = time.time()
			start2 = time.time()

			while True:
				#renew Temporary Exposure key every 5 minutes (24 hours)
				if (time.time() - start1) >= 5 * 60: #24 * 3600
					TEKey = generate_temp_exp_key()
					start1 = time.time()
					print(f'Key change: {TEKey.hex()}')
					print(f"[+] Today's Temporary Key: {TEKey.hex()}")
					update_generated_file(TEKey, working_location+'/database_files')
					random_id = generate_random_id(TEKey)
					meta = generate_metadata(TEKey, random_id)
					mac_address = secrets.token_hex(6)
					

				#renew random id, metadata and mac address every minute (15 minutes) 
				if (time.time() - start2) >= 60: #15 * 60
					random_id = generate_random_id(TEKey)
					meta = generate_metadata(TEKey, random_id)
					mac_address = secrets.token_hex(6)
					start2 = time.time()

					print(f"[+] Exposure data change\n\tid: {random_id}\n\tMAC address: {mac_address}\n\tMetadata: {meta}")

				#transmit beacon frames
				transmit_beacon(random_id, mac_address, meta)

		else:
			sys.exit('[!] App dependencies not met. Please check your installation')
	else:
		sys.exit('[!] Permission is required to detect exposures')



if __name__ == "__main__":
	#get current directory location
	work_area = os.getcwd()

	#create a directory to store random ids
	if not os.path.exists(work_area+'/database_files'):
		os.system('mkdir database_files')

	broadcast(work_area)


  
