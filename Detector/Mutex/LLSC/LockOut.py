import random
import threading
from time import sleep

from Detector.Mutex.LLSC import RuleSet
import RuleSet
import StatusMapping

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


def execute_rule_without_lock(rule):
    """
    执行单条规则，不申请设备锁。
    """
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    action_devices = rule["Action"]

    try:
        # 模拟规则执行
        print(f"Executing rule {ruleid}...")
        sleep(random.uniform(1.5, 2))

        # 更新全局状态字典
        with device_status_lock:  # 保留状态更新锁
            # 更新 trigger_device 的状态
            if trigger_device[0] in device_status:
                device_status[trigger_device[0]] = trigger_device[1]

            # 更新 action_device 的状态
            for action in action_devices:
                if action[0] in device_status:
                    device_status[action[0]] = action[1]

            # 记录规则执行顺序
            execution_order.append(ruleid)
    except Exception as e:
        print(f"Error executing rule {ruleid}: {e}")


def execute_all_rules_concurrently_without_lock(rules):
    """
    并发执行所有规则，不申请设备锁。
    """
    threads = []

    # 为每条规则创建一个线程
    for rule in rules:
        thread = threading.Thread(target=execute_rule_without_lock, args=(rule,))
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
rules = RuleSet.get_all_rules()
# 并发执行规则
execute_all_rules_concurrently_without_lock(rules)
# execution_order 和冲突检测
conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)

# 打印最终设备状态
print("\nFinal Device Status (Without Device Locks):")
for device, state in device_status.items():
    print(f"{device}: {state}")

# 打印规则执行顺序
print("\nExecution Order:")
print(execution_order)


# 打印冲突逆序对和数量
print("\nConflict Reverse Pairs:")
print(conflict_reverse_pairs)
print(f"\nTotal Number of Conflict Reverse Pairs: {len(conflict_reverse_pairs)}")
