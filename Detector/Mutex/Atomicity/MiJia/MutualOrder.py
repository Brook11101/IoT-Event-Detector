import base64
import hashlib
import hmac
import json
import os
import random
import time
from sys import platform
from threading import Thread
from time import sleep

import numpy as np
from Crypto.Cipher import ARC4
import matplotlib.pyplot as plt
import requests

if platform != "win32":
    import readline


# Redis 分布式锁封装
class RedisLock:
    def __init__(self, host='localhost', port=6379, password=None):
        """
        初始化 Redis 连接
        """
        import redis
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            decode_responses=True  # 自动将 Redis 的二进制数据解码为字符串
        )

    def acquire_lock(self, lock_name, retry_interval=0.1):
        """
        不断尝试获取分布式锁（没有超时时间）
        :param lock_name: 锁的名称（键）
        :param retry_interval: 每次重试的间隔时间（秒）
        :return: True（获取成功）
        """
        while True:
            result = self.client.set(lock_name, "locked", nx=True)  # 不设置过期时间
            if result:
                print(f"Lock acquired: {lock_name}")
                return True
            # print(f"Failed to acquire lock: {lock_name}, retrying...")
            time.sleep(retry_interval)

    def release_lock(self, lock_name):
        """
        释放分布式锁
        :param lock_name: 锁的名称（键）
        """
        self.client.delete(lock_name)
        print(f"Lock released: {lock_name}")


class XiaomiCloudConnector:

    def __init__(self, username, password, redis_lock):
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
        self.redis_lock = redis_lock

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
        param = {
            'data': json.dumps(
                {'params': [{'did': '134440830', 'siid': 2, 'piid': 2, 'value': value}]}
            ),
        }
        return self.execute_api_call_encrypted(url, param)

    def query_status(self, country):
        url = self.get_api_url(country) + "/miotspec/prop/get"
        param = {
            'data': json.dumps(
                {'params': [{'did': '134440830', 'siid': 2, 'piid': 2}], 'datasource': 1}
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
                                      verify="E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\Atomicity\MiJia\Data\Desktop.pem")
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


def worker(connector, country, value):
    """
    单个线程的工作逻辑：
    - 获取分布式锁
    - 执行 create_order
    - 查询状态，直到状态与期望值匹配
    - 释放分布式锁
    """
    lock_name = "lock:yeelight_bulb"

    # 获取分布式锁
    connector.redis_lock.acquire_lock(lock_name)

    try:
        # 记录请求发出的时间戳
        request_timestamp = time.perf_counter()  # 发出请求的时间戳
        # 执行请求
        result = connector.create_order(country, value)
        # 循环检查状态，直到状态与发送的 value 匹配
        while True:
            status = connector.query_status(country)
            status_dict = json.loads(status.decode('utf-8'))
            brightness = status_dict['result'][0]['value']
            print(f"Queried brightness: {brightness}, Expected value: {value}")
            if str(brightness) == str(value):  # 如果状态与发送的 value 一致
                print("Critical Section Kept. Releasing lock...")
                # 记录请求响应后的时间戳
                response_timestamp = time.perf_counter()  # 请求响应的时间戳
                # 打印发出请求时间戳和响应时间戳
                print(
                    f"Request sent at: {request_timestamp:.12f}, Response received at: {response_timestamp:.12f}, Value: {value}, Result: {result}"
                )
                break  # 跳出循环，准备释放锁
            else:
                print("Status mismatch. Retrying query_status...")
                time.sleep(1)  # 等待 1 秒后重试

    finally:
        # 释放分布式锁
        connector.redis_lock.release_lock(lock_name)


def crtiticalSectionTest():
    """
    测试函数：
    - 初始化 Redis 锁和 XiaomiCloudConnector
    - 创建多个线程并发调用 worker 函数
    """
    username = "2844532281"
    password = "whd123456"
    country = "cn"

    # 初始化 Redis 锁和连接器
    redis_lock = RedisLock(host='114.55.74.144', port=6379, password='whd123456')
    connector = XiaomiCloudConnector(username, password, redis_lock)

    print("Logging in...")
    if not connector.login():
        print("Login failed.")
        return
    print("Logged in.")

    # 设置测试参数
    frequency = 101  # 并发线程数
    threads = []

    # 创建并启动线程
    for value in range(1, frequency):
        thread = Thread(target=worker, args=(connector, country, value))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All threads completed.")


if __name__ == "__main__":
    crtiticalSectionTest()
