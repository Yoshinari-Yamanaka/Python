#-*- encoding:utf-8 -*-
import base64
import urllib.parse
from datetime import datetime,timedelta,timezone
import hashlib
import hmac

str_data = "あ"
# str -> bytes
encoded = str_data.encode("UTF-8") #b'\xe3\x81\x82'
# bytes -> hex
hex_str = encoded.hex() #"e38182"
# hex -> bytes
encoded = bytes.fromhex(hex_str) #b'\xe3\x81\x82'
# bytes -> base64
base64_str = base64.b64encode(encoded) #b'44GC'
# base64 -> bytes
encoded = base64.b64decode(base64_str) #b'\xe3\x81\x82'
# bytes -> str
str_data = encoded.decode() #"あ"
# str -> urlencode
urlencoded = urllib.parse.quote(str_data) #'%E3%81%82'
# urlencode -> str
str_data = urllib.parse.unquote(urlencoded) #"あ"

# str -> int
unicode = ord(str_data) #12354
# int -> hex
hex_str = hex(unicode) #'0x3042'
# hex -> int
unicode = int(hex_str,16) #12354
# int -> binary
binary = bin(unicode) #'0b11000001000010'
# binary -> int
unicode = int(binary,2) #12354
# int -> octal
oct_str = oct(unicode) #'0o30102'
# octal -> int
unicode = int(oct_str,8) #12354
# int -> str
str_data = chr(unicode) #"あ"

# normal Hash
data = 'python'
md5 = hashlib.md5(data.encode("UTF-8")).hexdigest()
sha256 = hashlib.sha256(data.encode("UTF-8")).hexdigest()
sha512 = hashlib.sha512(data.encode("UTF-8")).hexdigest()

# HMAC Hash
key = "secret key"
text = "Hello World!"
res = hmac.new(bytearray(key,"UTF-8"),bytearray(text,"UTF-8"),hashlib.sha256).hexdigest()

now = 'datetime.now()'
print(eval(now))