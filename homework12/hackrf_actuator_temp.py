#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 12
Name: Nikita Filin
'''

import zmq
import time, os
from datetime import datetime
import subprocess

def configure_doorbell():
	#can check if file exist before running
	if not os.path.exists("emos838"):
		print("[+] Configuring doorbell. Press transmitter button (Ctrl + C to exit)")
		os.system(f"hackrf_transfer -r emos838 -f 433500000 -s 2000000 -g 40")
		print("[+] Configuration complete")
	else:
		print("[+] Doorbell is already configured")


def ring_doorbell():
	print("[+] Ringing doorbell with hackrf_transfer")
	

	try:
		filename = "emos838"
		command = f"hackrf_transfer -t {filename} -f 433500000 -s 2000000 -l 24 -x 24"
		subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
		success = True

	except Exception as e:
		success = False
	update_actuator_log(success)


def update_actuator_log(success):
	print(f"[+] Updating doorbell log")
	
	now = datetime.now()
	date = now.strftime("%Y/%m/%d")
	
	time_str = now.strftime("%H:%M:%S")

	if success:
		log_string = f"\t{time_str}\tDoorbell Ring Success"
	else:
		log_string = f"\t{time_str}\tDoorbell Ring Failed"

	f = open(f"./logs/doorbell.log", "a+")

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
socket.bind("tcp://*:5556")

while True:
	#get command from processor
	command = socket.recv().decode()
	#if command ring then ring doorbell
	if command == "ring":
		configure_doorbell()
		ring_doorbell()


	time.sleep(5)

