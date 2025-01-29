import json
import random
import threading
from datetime import datetime
from time import sleep, time

import mysql
import RuleSet
from DBMyISAM import insert_log, clear_table
from Detector.Mutex.LLSC import StatusMapping

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

# -----------------------
# 全局数组，用于记录每个线程的执行时间 + 线程安全锁
thread_execution_times = []


def execute_rule(rule):
    """
    执行单条规则，将数据插入数据库，并记录本线程的执行时间。
    """

    # 获取规则的各项数据
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    condition_device = rule["Condition"]
    action_device = rule["Action"]
    description = rule["description"]
    lock_device = rule["Lock"]

    # 当前请求的执行开始时间: 仅用于插入日志（原逻辑）
    start_timestamp = time()
    # 记录线程开始时间
    start_time = time()

    # 模拟触发到执行的延迟
    sleep(random.uniform(1, 2))
    # 将数据插入数据库
    exec_time = insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, start_timestamp,
               start_time)

    thread_execution_times.append(exec_time)


def execute_all_rules_concurrently(rules):
    """
    并发执行所有规则（LockFree模式），
    在本函数中，我们只是启动所有线程并等待它们结束。
    """
    threads = []

    # 启动每个规则对应的线程
    for rule in rules:
        thread = threading.Thread(target=execute_rule, args=(rule,))
        threads.append(thread)
        thread.start()

    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()


def get_device_status():
    """
    从数据库读取日志记录，计算最终设备状态。
    """
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
            SELECT * FROM rule_execution_log_myisam
            WHERE status = TRUE
            ORDER BY logid ASC
        """)
        logs = cursor.fetchall()

        # 更新设备状态
        for log in logs:
            # 更新 trigger_device 的状态
            trigger_device = log["trigger_device"]
            if trigger_device:
                trigger_device_data = json.loads(trigger_device)
                if trigger_device_data[0] in device_status_result:
                    device_status_result[trigger_device_data[0]] = trigger_device_data[1]

            # 更新 action_device 的状态
            action_device = log["action_device"]
            if action_device:
                action_device_data = json.loads(action_device)
                for device, state in action_device_data:
                    if device in device_status_result:
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
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db"
        )
        cursor = connection.cursor(dictionary=True)

        # 查询 status = TRUE 的日志，并按时间戳排序
        cursor.execute("""
            SELECT ruleid FROM rule_execution_log_myisam
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
    conflict_dict = StatusMapping.rule_conflict_map
    conflict_reverse_pairs = []

    n = len(execution_order)
    for i in range(n):
        for j in range(i + 1, n):
            rule_i = execution_order[i]
            rule_j = execution_order[j]

            if rule_j < rule_i:
                if rule_i in conflict_dict.get(rule_j, set()):
                    conflict_reverse_pairs.append((rule_i, rule_j))

    return conflict_reverse_pairs


def run_experiment():
    """
    LockFree 模式下的实验。
    每组规则执行 20 轮，每轮记录冲突数量到 conflict_file，记录所有线程执行时间到 time_file。
    """
    base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\LLSC\Data\LockFree"

    for group_number in range(1, 6):
        # 获取对应分组规则
        group_rules = getattr(RuleSet, f"Group{group_number}")
        conflict_file = f"{base_path}\\num_lockfree_group_{group_number}.txt"
        time_file = f"{base_path}\\time_lockfree_group_{group_number}.txt"

        with open(conflict_file, "w") as conflict_output, open(time_file, "w") as time_output:
            for round_number in range(20):
                # 1) 清空数据库中的旧记录
                clear_table()

                # 2) 重置全局变量
                global thread_execution_times
                thread_execution_times = []  # 本轮所有线程执行时间清空

                # 3) 并发执行所有规则
                execute_all_rules_concurrently(group_rules)

                # 4) 获取执行顺序，冲突数量
                execution_order = get_execution_order()
                conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)
                conflict_count = len(conflict_reverse_pairs)

                # 5) 将冲突数量写入文件
                conflict_output.write(f"{conflict_count}\n")

                # 6) 将本轮所有线程执行时间(逗号分隔)写入文件
                times_str = ",".join(f"{t:.4f}" for t in thread_execution_times)
                time_output.write(times_str + "\n")

                print(f"Group {group_number}, Round {round_number + 1}: "
                      f"{conflict_count} conflicts")


if __name__ == "__main__":
    run_experiment()
