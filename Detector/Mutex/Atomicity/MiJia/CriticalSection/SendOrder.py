import base64
import gzip
import hashlib
import hmac
import json
import os
import random
import time
from sys import platform
from Crypto.Cipher import ARC4

import requests

if platform != "win32":
    import readline


class XiaomiCloudConnector:

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._agent = self.generate_agent()
        self._device_id = self.generate_device_id()
        self._session = requests.session()
        self._sign = None
        self._ssecurity = None
        self._userId = None
        self._cUserId = None
        self._passToken = None
        self._location = None
        self._code = None
        self._serviceToken = None

    def login_step_1(self):
        url = "https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true"
        headers = {
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        cookies = {
            "userId": self._username
        }
        response = self._session.get(url, headers=headers, cookies=cookies)
        valid = response.status_code == 200 and "_sign" in self.to_json(response.text)
        if valid:
            self._sign = self.to_json(response.text)["_sign"]
        return valid

    def login_step_2(self):
        url = "https://account.xiaomi.com/pass/serviceLoginAuth2"
        headers = {
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {
            "sid": "xiaomiio",
            "hash": hashlib.md5(str.encode(self._password)).hexdigest().upper(),
            "callback": "https://sts.api.io.mi.com/sts",
            "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
            "user": self._username,
            "_sign": self._sign,
            "_json": "true"
        }
        response = self._session.post(url, headers=headers, params=fields)
        valid = response is not None and response.status_code == 200
        if valid:
            json_resp = self.to_json(response.text)
            valid = "ssecurity" in json_resp and len(str(json_resp["ssecurity"])) > 4
            if valid:
                self._ssecurity = json_resp["ssecurity"]
                self._userId = json_resp["userId"]
                self._cUserId = json_resp["cUserId"]
                self._passToken = json_resp["passToken"]
                self._location = json_resp["location"]
                self._code = json_resp["code"]
            else:
                if "notificationUrl" in json_resp:
                    print("Two factor authentication required, please use following url and restart extractor:")
                    print(json_resp["notificationUrl"])
                    print()
        return valid

    def login_step_3(self):
        headers = {
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self._session.get(self._location, headers=headers)
        if response.status_code == 200:
            self._serviceToken = response.cookies.get("serviceToken")
        return response.status_code == 200

    def login(self):
        self._session.cookies.set("sdkVersion", "accountsdk-18.8.15", domain="mi.com")
        self._session.cookies.set("sdkVersion", "accountsdk-18.8.15", domain="xiaomi.com")
        self._session.cookies.set("deviceId", self._device_id, domain="mi.com")
        self._session.cookies.set("deviceId", self._device_id, domain="xiaomi.com")
        if self.login_step_1():
            if self.login_step_2():
                if self.login_step_3():
                    return True
                else:
                    print("Unable to get service token.")
            else:
                print("Invalid login or password.")
        else:
            print("Invalid username.")
        return False

    def create_order(self, country, value):
        url = self.get_api_url(country) + "/miotspec/prop/set"
        # 将嵌套的 data["data"] 转换为 JSON 字符串
        param = {
            'data': json.dumps(
                {'params': [{'did': '134440830', 'siid': 2, 'piid': 2, 'value': value}]}
            ),
        }
        return self.execute_api_call_encrypted(url, param)

    def execute_api_call_encrypted(self, url, params):
        proxies = {
            "http": "http://127.0.0.1:8888",
            "https": "http://127.0.0.1:8888",
        }
        headers = {
            "Accept-Encoding": "identity",
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2",
            "MIOT-ENCRYPT-ALGORITHM": "ENCRYPT-RC4",
        }
        cookies = {
            "userId": str(self._userId),
            "yetAnotherServiceToken": str(self._serviceToken),
            "serviceToken": str(self._serviceToken),
            "locale": "en_GB",
            "timezone": "GMT+02:00",
            "is_daylight": "1",
            "dst_offset": "3600000",
            "channel": "MI_APP_STORE"
        }
        millis = round(time.time() * 1000)
        nonce = self.generate_nonce(millis)
        signed_nonce = self.signed_nonce(nonce)
        fields = self.generate_enc_params(url, "POST", signed_nonce, nonce, params, self._ssecurity)
        response = self._session.post(url, headers=headers, cookies=cookies, params=fields, proxies=proxies,
                                      verify="E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\Atomicity\MiJia\CriticalSection\Data\Desktop.pem")
        if response.status_code == 200:
            decoded = self.decrypt_rc4(self.signed_nonce(fields["_nonce"]), response.text)
            return decoded
        return None

    def get_api_url(self, country):
        return "https://" + ("" if country == "cn" else (country + ".")) + "core.api.io.mi.com/app"

    def signed_nonce(self, nonce):
        hash_object = hashlib.sha256(base64.b64decode(self._ssecurity) + base64.b64decode(nonce))
        return base64.b64encode(hash_object.digest()).decode('utf-8')

    @staticmethod
    def generate_nonce(millis):
        nonce_bytes = os.urandom(8) + (int(millis / 60000)).to_bytes(4, byteorder='big')
        return base64.b64encode(nonce_bytes).decode()

    @staticmethod
    def generate_agent():
        agent_id = "".join(map(lambda i: chr(i), [random.randint(65, 69) for _ in range(13)]))
        return f"Android-7.1.1-1.0.0-ONEPLUS A3010-136-{agent_id} APP/xiaomi.smarthome APPV/62830"

    @staticmethod
    def generate_device_id():
        return "".join(map(lambda i: chr(i), [random.randint(97, 122) for _ in range(6)]))

    @staticmethod
    def generate_signature(url, signed_nonce, nonce, params):
        signature_params = [url.split("com")[1], signed_nonce, nonce]
        for k, v in params.items():
            signature_params.append(f"{k}={v}")
        signature_string = "&".join(signature_params)
        signature = hmac.new(base64.b64decode(signed_nonce), msg=signature_string.encode(), digestmod=hashlib.sha256)
        return base64.b64encode(signature.digest()).decode()

    @staticmethod
    def generate_enc_signature(url, method, signed_nonce, params):
        signature_params = [str(method).upper(), url.split("com")[1].replace("/app/", "/")]
        for k, v in params.items():
            # 作为字符串填进去
            signature_params.append(f"{k}={v}")
        signature_params.append(signed_nonce)
        signature_string = "&".join(signature_params)
        return base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode()

    @staticmethod
    def generate_enc_params(url, method, signed_nonce, nonce, params, ssecurity):
        # rc4_hash__是第一次根据params数组里面所有内容生成的base64编码的sha1算法加密摘要
        params['rc4_hash__'] = XiaomiCloudConnector.generate_enc_signature(url, method, signed_nonce, params)
        for k, v in params.items():
            params[k] = XiaomiCloudConnector.encrypt_rc4(signed_nonce, v)
        params.update({
            # 在通过第一次signature获得了rc4_hash__后，将params数组中的其他参数全部加密并且据此生成一个新的签名
            'signature': XiaomiCloudConnector.generate_enc_signature(url, method, signed_nonce, params),
            'ssecurity': ssecurity,
            '_nonce': nonce,
        })
        return params

    @staticmethod
    def to_json(response_text):
        return json.loads(response_text.replace("&&&START&&&", ""))

    @staticmethod
    def encrypt_rc4(password, payload):
        r = ARC4.new(base64.b64decode(password))
        r.encrypt(bytes(1024))
        return base64.b64encode(r.encrypt(payload.encode())).decode()

    @staticmethod
    def decrypt_rc4(password, payload):
        r = ARC4.new(base64.b64decode(password))
        r.encrypt(bytes(1024))
        return r.encrypt(base64.b64decode(payload))


def print_tabbed(value, tab):
    print(" " * tab + value)


def print_entry(key, value, tab):
    if value:
        print_tabbed(f'{key + ":": <10}{value}', tab)


username = "2844532281"
password = "whd123456"
servers = ["cn"]

connector = XiaomiCloudConnector(username, password)
print("Logging in...")
logged = connector.login()
if logged:
    print("Logged in.")
    print()
    for current_server in servers:
        result = connector.create_order(current_server, 100)
        if result is not None:
            print(result)
        else:
            print(f"Unable to make order from server {current_server}.")
else:
    print("Unable to log in.")
