import json
import random
import threading
from datetime import datetime
from time import sleep

import mysql

import RuleSet
from DataBase import insert_log  # 假设插入函数在 DataBase 模块里
from DataBase import clear_table
from Detector.Mutex.LLSC import StatusMapping


def execute_rule(rule, start_timestamp):
    """
    执行单条规则，将数据插入数据库
    """

    # 获取规则的各项数据
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    condition_device = rule["Condition"]
    action_device = rule["Action"]
    description = rule["description"]
    lock_device = rule["Lock"]

    # 这里使用的是当前请求的执行开始时间，开始执行的时候，发现导致自己Trigger/Condition条件违反的规则已经执行了，那么自己就被取消
    start_timestamp = int(datetime.now().timestamp())

    # 在这里我把sleep的时间同一设置在了插入记录函数的调用前，这是因为放在这里用于模拟trigger触发到action命令收到间隔的时间，此时收到后再去判断是否真正执行
    sleep(random.uniform(1.5, 2.0))

    # 调用 insert_log 函数将数据插入数据库
    insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, start_timestamp)


def execute_all_rules_concurrently():
    """
    并发执行所有规则
    """
    # 获取所有规则
    rules = RuleSet.get_all_rules()

    # 创建线程列表
    threads = []

    # 为每个线程生成一个新的 timestamp
    start_timestamp = int(datetime.now().timestamp())  # 获取当前 Unix 时间戳（秒）

    # 为每条规则创建一个线程
    for rule in rules:
        thread = threading.Thread(target=execute_rule, args=(rule, start_timestamp))
        threads.append(thread)
        thread.start()

    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()


def get_device_status():
    """
    读取数据库日志记录，计算最终设备状态。
    :return: 最终设备状态字典 device_status_result
    """
    # 初始化设备状态结果字典，拷贝初始值
    device_status_result = deviceStatus.copy()

    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db"
        )
        cursor = connection.cursor(dictionary=True)

        # 按时间戳升序读取日志记录
        cursor.execute("""
            SELECT * FROM rule_execution_log
            WHERE status = TRUE
            ORDER BY logid ASC
        """)
        logs = cursor.fetchall()

        # 遍历每条日志记录，更新设备状态
        for log in logs:
            # 更新 trigger_device 的状态
            trigger_device = log["trigger_device"]
            if trigger_device:
                trigger_device_data = json.loads(trigger_device)
                if trigger_device_data[0] in device_status_result:  # 判断是否在 deviceStatus 中
                    device_status_result[trigger_device_data[0]] = trigger_device_data[1]

            # 更新 action_device 的状态（优先级更高）
            action_device = log["action_device"]
            if action_device:
                action_device_data = json.loads(action_device)
                for device, state in action_device_data:
                    if device in device_status_result:  # 判断是否在 deviceStatus 中
                        device_status_result[device] = state


    except mysql.connector.Error as e:
        print(f"Database error: {e}")

    finally:
        if connection.is_connected():
            connection.close()

    return device_status_result


def get_execution_order():
    """
    从数据库读取日志，生成执行顺序，仅包含 status = TRUE 的 ruleid。
    """
    execution_order = []
    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db"
        )
        cursor = connection.cursor(dictionary=True)

        # 查询 status 为 TRUE 的日志，并按时间戳排序
        cursor.execute("""
            SELECT ruleid FROM rule_execution_log
            WHERE status = TRUE
            ORDER BY logid ASC
        """)
        logs = cursor.fetchall()

        # 提取执行顺序
        execution_order = [log["ruleid"] for log in logs]

    except mysql.connector.Error as e:
        print(f"Database error while getting execution order: {e}")

    finally:
        if connection.is_connected():
            connection.close()

    return execution_order


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



# 定义设备状态的初始值（硬编码为 0）
deviceStatus = {
    "Smoke": 0,
    "Location": 0,
    "WaterLeakage": 0,
    "MijiaCurtain1": 0,
    "MijiaCurtain2": 0,
    "YeelightBulb": 0,
    "SmartThingsDoorSensor": 0,
    "MijiaDoorLock": 0,
    "RingDoorbell": 0,
    "iRobotRoomba": 0,
    "AlexaVoiceAssistance": 0,
    "PhilipsHueLight": 0,
    "MideaAirConditioner": 0,
    "NetatmoWeatherStation": 0,
    "YeelightCeilingLamp1": 0,
    "YeelightCeilingLamp2": 0,
    "YeelightCeilingLamp3": 0,
    "YeelightCeilingLamp5": 0,
    "YeelightCeilingLamp6": 0,
    "WemoSmartPlug": 0,
    "WyzeCamera": 0,
    "SmartLifePIRmotionsensor1": 0,
    "SmartLifePIRmotionsensor2": 0,
    "SmartLifePIRmotionsensor3": 0,
    "MijiaPurifier": 0,
    "MijiaProjector": 0,
    "Notification": 0
}


# 清空上一轮的执行记录
clear_table()
# 执行所有规则并发任务
execute_all_rules_concurrently()

# 获取规则执行顺序
execution_order = get_execution_order()
# 检测冲突逆序对
conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)

# 调用函数，获取设备状态
final_device_status = get_device_status()

# 打印结果
print("Final Device Status:")
for device, state in final_device_status.items():
    print(f"{device}: {state}")

# 打印规则执行顺序
print("\nExecution Order:")
print(execution_order)

# 打印冲突逆序对和数量
print("\nConflict Reverse Pairs:")
print(conflict_reverse_pairs)
print(f"\nTotal Number of Conflict Reverse Pairs: {len(conflict_reverse_pairs)}")
