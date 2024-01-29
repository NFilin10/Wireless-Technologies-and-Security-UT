#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Homework 12
Name: Nikita Filin
'''

import zmq
import time, os, datetime



work_area = os.getcwd()


if not os.path.exists(work_area+'/logs'):
	os.system('mkdir logs')


approved_uid_list = ['01020304', '04699982F05C80', '', '']



context = zmq.Context()

#communication with ACR sensor
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")

#communication with HackRF actuator
socket2 = context.socket(zmq.PUSH)
socket2.connect("tcp://localhost:5556")


socket3 = context.socket(zmq.PUSH)
socket3.connect("tcp://localhost:5557")

while True:

	uid = socket.recv().decode()
	print("[+] UID received")
	
	if uid in approved_uid_list:
		curr_time = datetime.datetime.now().time()
		start_time = datetime.time(9, 0)
		end_time = datetime.time(17, 0)
		if curr_time >= start_time and curr_time < end_time:
			socket2.send("ring".encode())
		else:
			socket3.send("blink".encode())
			print("[+] Sending LED command")
	else:
		socket3.send("buzz".encode())
		print("[+] Sending Buzz command")
	
	time.sleep(1)
