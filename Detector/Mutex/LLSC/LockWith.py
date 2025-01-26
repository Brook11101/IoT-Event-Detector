import random
import threading
from time import sleep
from Detector.Mutex.LLSC import RuleSet
import RuleSet
import StatusMapping


class FIFOLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.queue = []
        self.owner = None  # 记录当前持有锁的事件（线程）

    def async_acquire(self):
        """
        异步申请锁，只提交申请，返回一个事件用于后续轮询检查锁是否成功获取。
        """
        event = threading.Event()
        with self.lock:
            self.queue.append(event)
            # 通知所有等待线程队列已更新
            self.condition.notify_all()
        return event

    def try_acquire(self, event):
        """
        尝试获取锁：
          - 如果自己在队首，
          - 且当前没有其它线程持有锁(self.owner为None)，
          - 则获取成功，成为锁拥有者(self.owner=event)，并出队返回 True；
          - 否则返回 False。
        """
        with self.lock:
            # 如果队列不空, 且队首正好是自己的 event, 且锁还没人持有
            if self.queue and self.queue[0] == event and self.owner is None:
                self.owner = event
                self.queue.pop(0)  # 弹出队首
                return True
        return False

    def release(self):
        """
        释放锁，清除当前owner 并唤醒队列中的其他线程。
        """
        with self.lock:
            self.owner = None
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

# 全局数组，用于记录规则执行的顺序
execution_order = []

# 全局设备锁字典
device_locks = {device: FIFOLock() for device in device_status}
lock_acquire_guard = threading.Lock()  # 全局锁，保护异步申请窗口


def execute_rule(rule):
    """
    异步申请所有锁后执行规则
    """
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    action_devices = rule["Action"]
    condition_devices = rule.get("Condition", [])  # 获取 Condition，默认为空列表

    # 按字典序排序，避免死锁
    locks_to_acquire = sorted(
        [device for device in [trigger_device[0]]
         + ([condition_devices[0]] if condition_devices else [])  # 确保 Condition 存在且非空
         + [action[0] for action in action_devices] if device in device_status]
    )

    # 提交锁申请阶段
    events = {}
    with lock_acquire_guard:
        for device in locks_to_acquire:
            if device in device_locks:
                events[device] = device_locks[device].async_acquire()

    # 检查锁申请结果
    acquired_locks = set()
    while True:
        for device, event in events.items():
            if device not in acquired_locks and device_locks[device].try_acquire(event):
                acquired_locks.add(device)  # 锁成功获取

        # 所有锁成功获取后退出
        if len(acquired_locks) == len(locks_to_acquire):
            break

    try:
        sleep(random.uniform(1.5, 2))

        # 更新全局状态字典
        with device_status_lock:
            # 更新 trigger_device 的状态
            if trigger_device[0] in device_status:
                device_status[trigger_device[0]] = trigger_device[1]

            # 更新 action_device 的状态
            for action in action_devices:
                if action[0] in device_status:
                    device_status[action[0]] = action[1]

            # 模拟规则执行
            print(f"Executing rule {ruleid}...")
            execution_order.append(ruleid)

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


def find_conflict_reverse_pairs(execution_order):
    """
    检测 execution_order 中的冲突逆序对
    """
    # 获取冲突对字典
    conflict_dict = StatusMapping.find_rule_conflicts(RuleSet.get_all_rules())

    # 记录冲突逆序对
    conflict_reverse_pairs = []

    # 遍历 execution_order 中的所有逆序对
    n = len(execution_order)
    for i in range(n):
        for j in range(i + 1, n):  # 只看后面的规则，形成逆序对
            rule_i = execution_order[i]
            rule_j = execution_order[j]

            # 检测是否为逆序对 (rule_j 比 rule_i 早完成，但启动顺序晚)
            if rule_j < rule_i:
                # 对于找到的逆序对，要以小的id作为key值，检查大的id是否影响了小的id的规则
                if rule_i in conflict_dict.get(rule_j, set()):
                    conflict_reverse_pairs.append((rule_i, rule_j))

    return conflict_reverse_pairs

# 获取所有规则
rules = RuleSet.Group1
# 并发执行规则
execute_all_rules_concurrently(rules)
# execution_order 和冲突检测
conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)

# 打印最终设备状态
print("\nFinal Device Status (With Device Locks):")
for device, state in device_status.items():
    print(f"{device}: {state}")

# 打印规则执行顺序
print("\nExecution Order:")
print(execution_order)

# 打印冲突逆序对和数量
print("\nConflict Reverse Pairs:")
print(conflict_reverse_pairs)
print(f"\nTotal Number of Conflict Reverse Pairs: {len(conflict_reverse_pairs)}")
