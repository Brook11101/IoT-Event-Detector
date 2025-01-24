import threading
import time
import random
from time import sleep

from Detector.Mutex.LLSC import RuleSet


class FIFOLock:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def acquire(self):
        event = threading.Event()
        with self.lock:
            self.queue.append(event)
            while self.queue[0] is not event:
                self.condition.wait()
        event.set()

    def release(self):
        with self.lock:
            self.queue.pop(0)
            self.condition.notify_all()


# 全局状态字典
device_status = {
    "Smoke": 0, "Location": 0, "WaterLeakage": 0, "MijiaCurtain1": 0, "MijiaCurtain2": 0,
    "YeelightBulb": 0, "SmartThingsDoorSensor": 0, "MijiaDoorLock": 0, "RingDoorbell": 0,
    "iRobotRoomba": 0, "AlexaVoiceAssistance": 0, "PhilipsHueLight": 0, "MideaAirConditioner": 0,
    "NetatmoWeatherStation": 0, "YeelightCeilingLamp1": 0, "YeelightCeilingLamp2": 0,
    "YeelightCeilingLamp3": 0, "YeelightCeilingLamp5": 0, "YeelightCeilingLamp6": 0,
    "WemoSmartPlug": 0, "WyzeCamera": 0, "SmartLifePIRmotionsensor1": 0,
    "SmartLifePIRmotionsensor2": 0, "SmartLifePIRmotionsensor3": 0, "MijiaPurifier": 0,
    "MijiaProjector": 0, "Notification": 0
}
device_status_lock = threading.Lock()  # 确保 device_status 的线程安全

# 全局设备锁字典
device_locks = {device: FIFOLock() for device in device_status}


def execute_rule(rule):
    """
    执行单条规则
    """
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    action_devices = rule["Action"]

    # 按 FIFO 顺序申请 Trigger 和 Action 的锁
    locks_to_acquire = [trigger_device[0]] + [action[0] for action in action_devices]
    # 避免死锁
    locks_to_acquire = sorted(locks_to_acquire)

    # 申请所有需要锁的设备
    acquired_locks = []  # 记录已成功申请的锁
    for device in locks_to_acquire:
        if device in device_locks:  # 仅为需要锁的设备申请锁
            device_locks[device].acquire()
            acquired_locks.append(device)  # 记录已申请的锁

    try:
        # 模拟规则执行
        print(f"Executing rule {ruleid}...")
        sleep(random.uniform(1.5,2))
        # 更新全局状态字典
        with device_status_lock:
            # 更新 trigger_device 的状态
            if trigger_device[0] in device_status:
                device_status[trigger_device[0]] = trigger_device[1]

            # 更新 action_device 的状态
            for action in action_devices:
                if action[0] in device_status:
                    device_status[action[0]] = action[1]

    finally:
        # 释放所有已申请的锁
        for device in acquired_locks:
            device_locks[device].release()


def execute_all_rules_concurrently(rules):
    """
    并发执行所有规则
    """
    threads = []

    # 为每条规则创建一个线程
    for rule in rules:
        thread = threading.Thread(target=execute_rule, args=(rule,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()



# 获取所有规则
rules = RuleSet.get_all_rules()
# 并发执行规则
execute_all_rules_concurrently(rules)

# 打印最终设备状态
print("\nFinal Device Status:")
for device, state in device_status.items():
    print(f"{device}: {state}")
