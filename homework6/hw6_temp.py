#!/usr/bin/env python3

'''
Name: Nikita Filin
Wireless Technologies and Security (LTAT.04.009) Homework 6

Sample case:
-------------------------------------------------------------------------------
NETWORK_SSID = b'RockhunterHS'
NETWORK_PASS = b'uion7131'
ANonce = 'bae293bba5f6793db737bfa13728ccfb046cf9399527f905da3efbe4d90f9548'
SNonce = '60c906499b6124f0d8788785c3d03d0ee8724397397f3407bf8003f91fc80377'
AP_MAC = '888322bd6724'
Sta_MAC = '18e7f4c856ac'

PMK: 4bbf855400a1af638269b37e73b65e541fdfc799dd8f82ecf420c7d182c276d7
PTK: 878df35b5bdd8727e2dc6e69085734e283478911bcb8d96bfa9b2174157d7945191fc45c247d2a8951f213f187e6bce4c9793d484a4fac6c55c885309300ab42948663034a9721789a4df7a9b4f43c8d
KCK: 878df35b5bdd8727e2dc6e69085734e2
KEK: 83478911bcb8d96bfa9b2174157d7945
TK: 191fc45c247d2a8951f213f187e6bce4

'''
#no other imports needed
import hashlib, hmac


#complete function, produces an 80 byte key 
def calculatePTK(PMK, data):
    len = 384
    i = 0
    message = b''

    while i <= (len + 159)/160:
        message = message + hmac.new(PMK, b'Pairwise key expansion\x00' + data + chr(i).encode(), hashlib.sha1).digest()
        i+=1
    return message



if __name__ == "__main__":
    NETWORK_SSID = b'4way Example SSID'
    NETWORK_PASS = b'S0mething$imple'
    ANonce = '77f5bf3f0115ae761d63c9f2e1a7a41022c93c591888dd8c2c7f9e57d7604a1f'
    SNonce = '67fa21bc8f9d70303d107e44bd989bd47aaec9965d308be86bd07291674796cd'
    AP_MAC = '28ee524f48c4'
    Sta_MAC = 'f2ebd8db06e6'


    print(f'SSID: {NETWORK_SSID}\nPassphrase: {NETWORK_PASS}\nAnonce: {ANonce}\nSnonce: {SNonce}\nAP MAC: {AP_MAC}\nSTA MAC: {Sta_MAC}\n\n')

    '''
    https://docs.python.org/3/library/hashlib.html#key-derivation
    dklen should be in bytes
    PMK = PBKDF2(HMAC SHA1, passphrase, ssid, 4096, 32)
    https://www.wireshark.org/tools/wpa-psk.html 
    '''
    PMK = hashlib.pbkdf2_hmac('sha1', NETWORK_PASS, NETWORK_SSID, 4096, 32)
    print(f'PMK: {PMK.hex()}')

    '''
    MAC addresses are sorted then nonces are sorted
    https://docs.python.org/3/library/functions.html#max
    https://www.w3schools.com/python/ref_func_min.asp, https://www.w3schools.com/python/ref_func_max.asp
    '''
    message = bytearray.fromhex(min(AP_MAC, Sta_MAC)) + bytearray.fromhex(max(AP_MAC, Sta_MAC)) + bytearray.fromhex(min(SNonce, ANonce)) + bytearray.fromhex(max(SNonce, ANonce))

    PTK = calculatePTK(PMK, message)
    
    KCK = PTK[0:16]
    KEK = PTK[16:32]
    TK = PTK[32:48]

    print(f'PTK: {PTK.hex()}\nKCK: {KCK.hex()}\nKEK: {KEK.hex()}\nTK: {TK.hex()}')
