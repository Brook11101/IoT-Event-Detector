import json
import threading
from datetime import datetime
from turtledemo.penrose import start

import mysql

import RuleSet
from DataBase import insert_log  # 假设插入函数在 DataBase 模块里
from DataBase import clear_table

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
            ORDER BY timestamp ASC
        """)
        logs = cursor.fetchall()

        # 遍历每条日志记录，更新设备状态
        for log in logs:
            # 更新 trigger_device 的状态
            trigger_device = log["trigger_device"]
            if trigger_device:
                trigger_device_data = json.loads(trigger_device)
                device_status_result[trigger_device_data[0]] = trigger_device_data[1]

            # 更新 action_device 的状态（优先级更高）
            action_device = log["action_device"]
            if action_device:
                action_device_data = json.loads(action_device)
                for device, state in action_device_data:
                    device_status_result[device] = state


    except mysql.connector.Error as e:
        print(f"Database error: {e}")

    finally:
        if connection.is_connected():
            connection.close()

    return device_status_result


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
# 调用函数，获取设备状态
final_device_status = get_device_status()

# 打印结果
print("Final Device Status:")
for device, state in final_device_status.items():
    print(f"{device}: {state}")
