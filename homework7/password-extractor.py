#!/usr/bin/env python3

f_read = open("rockyou.txt", "rb")
f1_write = open("pcap2_pass.txt", "wb")
f2_write = open("pcap3_pass.txt", "wb")

for a_line in f_read:
	if chr(a_line[0]) == 'j':
		f2_write.write(a_line)
	if len(a_line) == 13:
		f2_write.write(a_line)
	if len(a_line) == 11:
		f1_write.write(a_line)

f_read.close()
f1_write.close()
f2_write.close()
