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
ssecurity = "LVRULY0nspoEBKgZ1bS73A=="
nonce = "dj23qk7b8pABuZzQ"
payload = "dIEPglnT/ZqRZjA64TYrn/oEd1nOFLgpHZOUt+t06bEjzS4vIEuK6UkJ/zciOx0mdk/kBTk3PtLSW2S8u2wIfnELFLLZDzhxhvi/oHz79SEfNVH7SlAANbLymsLqhIynFMRXaizGjrh9OQ2wcinvj65yt4YHTKzECnO9KL8ArIXA9qE8Xass9NvNlFdMY2q+wdd7DeIGAGgRRZr+Pn5jiiAguhoFU1z3GMTqEm5aMfqgSP7i7ojnMlhYcPMMAQi6nzji9VFoEsmlUtU593434kM+UOrc8fWxkA=="
response = "ECh34yuykOmzo8eOAjiBy9T4pB8E7i5VuznT+UeFDdorsmmhv9wQDJmUS1Q+pSsYeoRdle+v5AYI1nPP65rhNdyEKo9sE0F2fDEssu4EFN7yWSLym44eRtu9j67Pv48hEODNsww8cvT1m3etzqmief/aEBtZQoI0YQ71tKNiT55UMTfMcED5giB8MfwyGIz2dAGvwS2BOakrcL4wKoa0LCn6G/LvT8n0SBYBQnitSyVtgdrSzFs61/JzIpw0MyQ="
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