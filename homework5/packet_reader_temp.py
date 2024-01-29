#!/usr/bin/env python3

'''
Reads a pcap file and displays the management frames (and maybe control and data as well)

Wireless Technologies and Security (LTAT.04.009) Homework 5 template
Executing Script: sudo python3 packet_reader_temp.py
'''
import getopt
import sys

import colorama
from colorama import Fore, Style


BEACON_FRAME = [b'\x80', b'\x00']

channels = {
0:'undefined',
2412:'1',
2417:'2',
2422:'3',
2427:'4',
2432:'5',
2437:'6',
2442:'7',
2447:'8',
2452:'9',
2457:'10',
2462:'11',
2467:'12',
2472:'13',
2484:'14',
}

def formatMac(mac):
    mac = b''.join(mac)
    formatted = list(mac.hex())
    i = 2
    while i < len(formatted):
        formatted.insert(i,":")
        i=i+3

    return ''.join(formatted).upper()

def convertSSID(payload, ssidIndex):
    payload = b''.join(payload)

    ssidlength = payload[ssidIndex]
    ssid = payload[ssidIndex+1:ssidIndex+1+ssidlength]

    if ssidlength < 1:
        return "Wildcard (Broadcast)"
    else:
        try:
            return str(ssid, 'utf-8')
        except:
            return "Weird characters in SSID"

def findNetworkSpecs(packet):
    header_revision = packet[0]
    header_pad = packet[1]

    header_length = b''.join(packet[2:4])
    header_length = int.from_bytes(header_length, "little")

    present_flags = b''.join(packet[4:8])

    mac_timestamp = b''.join(packet[8:16])
    mac_timestamp = int.from_bytes(mac_timestamp, "little")
    
    flags = packet[16]
    data_rate = ord(packet[17])/2
    
    channel_frequency = b''.join(packet[18:20])
    channel_frequency = int.from_bytes(channel_frequency, "little")
    
    try:
        channel = channels[channel_frequency]
    except:
        channel = 'unknown'
    channel_flags = b''.join(packet[20:22])
    ant_signal = calcSignalStrength(packet[22])
    antennna = packet[23]
    rx_flags = b''.join(packet[24:26])

    if header_length > 26:
        mcs_info = packet[26:]


    RADIO_TAP_HEADER = {
    'version': [header_revision, header_pad],
    'length': header_length,
    'timestamp': str(mac_timestamp),
    'data rate': str(data_rate),
    'frequency': str(channel_frequency),
    'channel': channel,
    'antenna signal': str(ant_signal),
    }

    return RADIO_TAP_HEADER

def calcSignalStrength(signal):
    #convert hex from 2's complement
    rawValue = ord(signal)
    
    compare = 64 #bit compare number
    strength = -128 #starting value 2to7 is -128
    i =  6 #start adding from 2to6
    while i >= 0:
        if rawValue & compare:
            strength+=2**i
        i-= 1
        compare = compare >> 1
    return strength


#grab the next packet from the PCAP file
def get_Packet(start):
    packet_ts_sec = pcap_byte_array[start:start+4] #This is the number of seconds since the start of 1970
    packet_ts_usec = pcap_byte_array[start+4:start+8] #microseconds part of the time at which the packet was captured
    packet_incl_len = pcap_byte_array[start+8:start+12] #size of the saved packet data in our file in bytes
    packet_orig_len = pcap_byte_array[start+12:start+16] #these may have different values in cases where we set the maximum packet length

    length = 0

    if packet_incl_len == packet_orig_len:
        for i in range(3,-1, -1):
            length = length << 8
            length+=ord(packet_incl_len[i])
    elif packet_orig_len < packet_incl_len:
        for i in range(3,-1, -1):
            length = length << 8
            length+=ord(packet_orig_len[i])

    next_packet = length + start + 16
    return next_packet, pcap_byte_array[start+16:start+16+length]


'''
----------------------
Set file location here
----------------------
'''
# path_to_pcap = "./pcap/ctl_frames.pcap"
path_to_pcap = "./pcap/mgt_frames.pcap"
# path_to_pcap = "./pcap/test_pcap1.pcap"
# path_to_pcap = "./pcap/test_pcap2.pcap"
# path_to_pcap = "./pcap/test_pcap3.pcap"
# path_to_pcap = "./pcap/test_pcap4.pcap"

try:
    pcap_file = open(path_to_pcap,'rb')
except getopt.GetoptError:
    print('File not found')
    sys.exit(2)

not_at_end = True
pcap_byte_array = []

#convert pcap to byte array
while not_at_end:
    pcap_byte = pcap_file.read(1)

    if pcap_byte != b'':
        pcap_byte_array.append(pcap_byte)
    else:
        not_at_end = False

pcap_file.close()

print('\nNumber of bytes in pcap: {}'.format(len(pcap_byte_array)))

#pcap global header (first 24 bytes)
#https://wiki.wireshark.org/Development/LibpcapFileFormat
pcap_magic_number = pcap_byte_array[0:4] #used to detect the file format itself and the byte ordering
pcap_version_major = pcap_byte_array[4:6] #the version number of this file format (little endian)
pcap_version_minor = pcap_byte_array[6:8]
pcap_thiszone = pcap_byte_array[8:12] #the correction time in seconds between GMT
pcap_sigfigs = pcap_byte_array[12:16] #in theory, the accuracy of time stamps in the capture
pcap_snaplen = pcap_byte_array[16:20] #the "snapshot length" for the capture (typically 65535)
pcap_network = pcap_byte_array[20:24] #link-layer header type https://www.tcpdump.org/linktypes.html

#print('PCAP Info')
#print('Magic Number {}, \nVersion {}.{}, \nZone Correction: {}, \nSig Figs: {}, \nCapture Length: {}, \nNetwork Type: {}'.format(pcap_magic_number, pcap_version_major, pcap_version_minor, pcap_thiszone, pcap_sigfigs, pcap_snaplen, pcap_network))


#track location in pcap file list
tracker = 24


'''
----------------
Your coding starts here
----------------
'''


def print_info(frame_name, payload, ssid_index, bssid_need, color):
    color_code = getattr(Fore, color)
    print(color_code + frame_name)
    print("-" * 25)


    if bssid_need:
        BSSID = ''
        if (ord(frame_ctl[1]) & 3) == 0:
            BSSID = address_3
        elif (ord(frame_ctl[1]) & 3) == 1:
            BSSID = address_2
        elif (ord(frame_ctl[1]) & 3) == 2:
            BSSID = address_1
        print(f'BSSID: {formatMac(BSSID)}')

    if ssid_index != -1:
        SSID = convertSSID(payload, ssid_index)
        print(f'SSID: {SSID}')

    print(f'Channel: {RADIO_TAP_HEADER["channel"]}')
    print(f'Signal Strength: {RADIO_TAP_HEADER["antenna signal"]} dBm \n')


while tracker < len(pcap_byte_array):

    #get the next packet and the location in pcap file list
    tracker, packet = get_Packet(tracker)
    RADIO_TAP_HEADER = findNetworkSpecs(packet)

    if RADIO_TAP_HEADER['version'] == [b'\x00', b'\x00']: #radiotap header version 0
        ip_packet = packet[RADIO_TAP_HEADER['length']:] #strip off radiotap header

        if ip_packet != [b'\x00', b'\x00', b'\x00', b'\x00']: #ensure frame has valid data
            frame_ctl = ip_packet[0:2]
            address_1 = ip_packet[4:10]
            address_2 = ip_packet[10:16]
            address_3 = ip_packet[16:22]
            payload = ip_packet[24:-4]

            if (ord(frame_ctl[0]) & 12) == 0:
                if (ord(frame_ctl[0]) & 240) == 64:
                    print_info("Probe request", payload, 1, False, "BLUE")

                elif (ord(frame_ctl[0]) & 240) == 80:
                    print_info("Probe response", payload, 13, True, "BLUE")

                elif (ord(frame_ctl[0]) & 240) == 176:
                    print_info("Authentication", payload, -1, True, "GREEN")

                elif (ord(frame_ctl[0]) & 240) == 192:
                    print_info("Deauthentication", payload, -1, True, "GREEN")

                elif (ord(frame_ctl[0]) & 240) == 0:
                    print_info("Association Request", payload, 13, True, "YELLOW")

                elif (ord(frame_ctl[0]) & 240) == 16:
                    print_info("Association Response", payload, -1, True, "YELLOW")

                elif (ord(frame_ctl[0]) & 240) == 32:
                    print_info("Re-association Request", payload, 11, True, "RED")

                elif (ord(frame_ctl[0]) & 240) == 48:
                    print_info("Re-association Response", payload, -1, True, "RED")

                elif (ord(frame_ctl[0]) & 240) == 160:
                    print_info("Disassociation", payload, -1, True, "MAGENTA")

                elif (ord(frame_ctl[0]) & 240) == 208:
                    print_info("Action", payload, -1, True, "MAGENTA")





