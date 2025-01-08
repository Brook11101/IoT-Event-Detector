import base64
import hashlib
import hmac
import json
import os
import random
import time
import gzip
from sys import platform
from Crypto.Cipher import ARC4



# 加密解密算法
ssecurity = "V0XVCBIwJnvt8uegdMOMbA=="
nonce = "BP3GsinfhyEBuY1t"
payload = "XvWh2747oqwg8jPvj3izWv9Ob5L2Lx29KxaMpSFkzksbj360TZqjSesKxtCKCnv0S6M1zK+klaoEEbSxTg=="
response = "OlzZusxaz98CN8LC59KVd4jGf3OU0WSkNWDz2lb6vvK9sMjHXeKiRVZK/gYinh+SoJkFEojzg6YBFPhcAywC6e627LLUTYho3qJvLuNKOPaxQYgk/De/53O3htYEZRb5kQOkdk/O5C7RjiQ+pIAFgQ=="
hash_object = hashlib.sha256(base64.b64decode(ssecurity) + base64.b64decode(nonce))
signed_nonce = base64.b64encode(hash_object.digest()).decode('utf-8')
r1 = ARC4.new(base64.b64decode(signed_nonce))
r1.encrypt(bytes(1024))
r2 = ARC4.new(base64.b64decode(signed_nonce))
r2.encrypt(bytes(1024))

print("send message:")
send_message = r1.encrypt(base64.b64decode(payload))
print(json.loads(send_message))
print()

print("response message:")
response_message = r2.encrypt(base64.b64decode(response))
print(gzip.decompress(response_message).decode('utf-8'))