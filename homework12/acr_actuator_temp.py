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



def execute_command(state, on_time, off_time, reps, buzzer):
	r=readers()
	connection = r[0].createConnection()
	connection.connect()

	acr1252_control = [0xFF, 0x00, 0x40, state, 0x04, on_time, off_time, reps, buzzer] 
	data, sw1, sw2 = connection.transmit(acr1252_control)

	if sw1 == 0x90:
		return 1
	else:
		return 0
	


def update_reader_log(msg):
	print(f"[+] Updating reader log")

	now = datetime.now()
	date = now.strftime("%Y/%m/%d")
	
	time_str = now.strftime("%H:%M:%S")

	f = open(f"./logs/reader.log", "a+")

	log_string = f"\t{time_str}\t{msg}"

	f.seek(0)
	content = f.read()

	if date in content:
		f.write(log_string+"\n")
	else:
		f.write(f"{date}\n")
		f.write(log_string+"\n")




	f.close()


#configure sockets
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5557")

while True:
	command = socket.recv().decode()
	if command == "blink":
		print("[+] LED blink")
		status = execute_command(0xFC, 0x04, 0x01, 0x05, 0x00)
		if status == 1:
			update_reader_log("Orange LED Blink Success")
		else:
			update_reader_log("Orange LED Blink Failed")
	
	elif command == "buzz":
		print("[+] Buzzer")
		status = execute_command(0x00, 0x01, 0x01, 0x03, 0x03)
		if status == 1:
			update_reader_log("Buzzer Success")
		else:
			update_reader_log("Buzzer Failed")

	

	time.sleep(5)

	