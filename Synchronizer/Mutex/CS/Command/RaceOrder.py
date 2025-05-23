import base64
import gzip
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
import numpy as np

import requests

if platform != "win32":
    import readline



# 功能性的对照实验，说明MiJia服务器在接收高并发请求的时候没有做到互斥性处理
# 但是没啥用，mutex的功能性不通过这一点来证明

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

    def query_status(self, country):
        url = self.get_api_url(country) + "/miotspec/prop/get"
        # 将嵌套的 data["data"] 转换为 JSON 字符串
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


def worker(connector, country, value):
    # 记录请求发出的时间戳
    request_timestamp = time.perf_counter()  # 发出请求的时间戳
    # 执行请求
    result = connector.create_order(country, value)
    # 记录请求响应后的时间戳
    response_timestamp = time.perf_counter()  # 请求响应的时间戳
    # 打印发出请求时间戳和响应时间戳
    print(
        f"Request sent at: {request_timestamp:.12f}, Response received at: {response_timestamp:.12f}, Value: {value}, Result: {result}")
    return request_timestamp, response_timestamp, value, result


def crtiticalSectionTest(frequency, rounds):
    username = "2844532281"
    password = "whd123456"
    country = "cn"

    connector = XiaomiCloudConnector(username, password)
    print("Logging in...")
    if not connector.login():
        print("Login failed.")
        return
    print("Logged in.")

    all_results = {}

    for freq in range(1, frequency + 1, 10):  # frequency: 1, 11, 21, ..., 101
        if freq == 101:
            freq = 100
        all_results[freq] = {"true_count": 0, "false_count": 0}

        for round_num in range(rounds):  # 进行 20 轮实验
            threads = []
            results = []  # 用于存储每轮的结果

            def worker_with_timestamp(connector, country, value):
                request_timestamp, response_timestamp, value, result = worker(connector, country, value)
                results.append((request_timestamp, response_timestamp, value, result))  # 保存时间戳、值和结果

            for value in range(1, freq + 1):  # 规则并发数freq次
                thread = Thread(target=worker_with_timestamp, args=(connector, country, value))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # 按时间戳排序结果
            results.sort(key=lambda x: x[0])

            # 打印本轮结果
            print("All threads completed. Results:")
            for request_timestamp, response_timestamp, value, result in results:
                print(
                    f"Request Timestamp: {request_timestamp:.12f}, Response Timestamp: {response_timestamp:.12f}, Value: {value}, Result: {result}")

            sleep(5)

            status = connector.query_status(country)
            status_dict = json.loads(status.decode('utf-8'))
            brightness = status_dict['result'][0]['value']
            print(f"Brightness: {brightness}")

            final_brightness = results[-1][2]  # 获取最后一项的 value
            if final_brightness == brightness:
                print("True")
                all_results[freq]["true_count"] += 1  # 记录 true 的数量
            else:
                print("False")
                all_results[freq]["false_count"] += 1  # 记录 false 的数量

        # 输出当前频率实验的统计结果
        print(f"Results for frequency = {freq}:")
        print(f"True count: {all_results[freq]['true_count']}, False count: {all_results[freq]['false_count']}")
        print("-" * 40)

    # 绘制图形
    frequencies = list(all_results.keys())
    true_counts = [all_results[freq]["true_count"] for freq in frequencies]
    false_counts = [all_results[freq]["false_count"] for freq in frequencies]

    plt.figure(figsize=(10, 6))
    width = 0.35  # 条形图的宽度
    x = np.arange(len(frequencies))  # x轴的位置

    # 绘制 true 和 false 的条形图
    plt.bar(x - width / 2, true_counts, width, label="True", color='g')
    plt.bar(x + width / 2, false_counts, width, label="False", color='r')

    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.title('True/False Count for Each Frequency')
    plt.xticks(x, frequencies)  # 设置x轴的刻度为频率
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    frequency = 101  # 最大频率值 (100)
    rounds = 20  # 每个频率进行 20 轮实验
    crtiticalSectionTest(frequency, rounds)
