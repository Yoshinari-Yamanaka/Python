# -*- encoding: utf-8 -*-
import base64
from datetime import datetime,timedelta,timezone
import hashlib
import json
import os
import sys
import urllib.parse
#Third Party
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Padding
from Crypto.Protocol.KDF import PBKDF2


# Initial Vector length should be 16 bytes length
JST = timezone(timedelta(hours=9),"JST")
now = hex(int(datetime.now(JST).timestamp()))
hs = hashlib.sha512(now.encode()).hexdigest()
IV = bytes.fromhex(hs[0:100])[:AES.block_size]

# Salt. The hexadecimal characters should be even numbers to be converted to bytes object. And it's OK any length
SALT = bytes.fromhex("39ccc779ab356eb43b4f37aedbc891d2f891756710b7856d21a2fd691483fb17")

# The secret password or pass phrase to generate the key from.
SECRET_KEY = "asd@dfdfdsds"

# The number of iterations to carry out. It's recommended to use at least 1000.
SECURE_LEVELS = 1000

# padding
PADDING_ALGORITHM = "pkcs7"

def encrypt(plainText):    
    # create PBKDF2 　　16 bytes(AES-128), 24 bytes(AES-192), 32bytes(AES-256)
    key = PBKDF2(password=SECRET_KEY, salt=SALT, dkLen=16, count=SECURE_LEVELS)
    
    # cipher
    cipher = AES.new(key, AES.MODE_CBC, IV)

    # Padding
    data = plainText.encode()
    if "pkcs7" == PADDING_ALGORITHM:
        data = Padding.pad(data, AES.block_size, 'pkcs7')
    else:
        padding = AES.block_size - len(data) % AES.block_size
        data += (chr(padding) * padding).encode()
    
    # encrypt
    encrypted = cipher.encrypt(data)
    
    # bytes -> Hexadecimal
    hex_data = encrypted.hex()

    # Hexadecimal -> Base64
    base64_encoded = base64.b64encode(hex_data.encode())  
    url_encoded = urllib.parse.quote(base64_encoded)

    return url_encoded


def decrypt(encrypted):
    # decode URL encoded value
    url_decoded = urllib.parse.unquote(encrypted)

    # Base64 -> Hexadecimal
    base64_decoded = base64.b64decode(url_decoded).decode()
    
    # Hexadecimal -> bytes
    encrypted = bytes.fromhex(base64_decoded)
  
    # create PBKDF2
    key = PBKDF2(password=SECRET_KEY, salt=SALT, dkLen=16, count=SECURE_LEVELS)

    # cipher
    cipher = AES.new(key, AES.MODE_CBC, IV)

    # decrypt
    decrypted = cipher.decrypt(encrypted)
    if "pkcs7" == PADDING_ALGORITHM:
        response = Padding.unpad(decrypted, AES.block_size, 'pkcs7').decode("utf-8")
    else:
        # bytes object show itself as a hexademical.
        # And it's seequential object that each ones are seems to be a decimal
        # ex) b'\xe3\x81\x82'[-1]  ->  130  (this is same value as hexadecimal 82)
        response = decrypted[: -int(decrypted[-1])].decode('utf-8')
    return response


if __name__ == "__main__":
    """
    encrypt
    """
    plainText = "これは平文です"
    print("Plain text".ljust(15) + f"= {plainText}")
    encrypted = encrypt(plainText)
    
    """
    decrypt
    """
    #sample query parameter
    parsed = f"key=value&ID={encrypted}&resolution=1920x1080"
    parsed = urllib.parse.parse_qs(parsed)
    
    decrypted_data = decrypt(parsed["ID"][0])
    print("decrypted_data".ljust(15) + f"= {decrypted_data}")