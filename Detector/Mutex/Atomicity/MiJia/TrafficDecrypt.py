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
ssecurity = "/FTz8LBej2KWgJZNwmL6Eg=="
nonce = "BuDltcTWZu4BuZht"
payload = "ry75xm4gi7xHUWII78dpuHKO/zBNRhgsuTH+tGWC+X7cnFCTaM0MAemoscGjerckd2NaYfMH2ZBbqG0W0BNlr1Jel9g="
# response = "m91///jyY9hivddFbR/JerNQJEfSvlVp+CUf0X7WFwbikM1RjfYVW0SvP5F9E5FuPhmTYQjIujw8bK5KGZ3YgTuYO7sloVqzReSjLHpf9Q0EjBc9Dxm4c4vF2Q0rtUERDXTEgHiqgtY6vSsfIWw="
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

# print("response message:")
# response_message = r2.encrypt(base64.b64decode(response))
# print(gzip.decompress(response_message).decode('utf-8'))