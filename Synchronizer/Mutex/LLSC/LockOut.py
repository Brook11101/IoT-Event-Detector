import random
import threading
from time import sleep, time
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

# 记录规则执行的顺序
execution_order = []

# （新增）记录每个线程执行时间的列表 + 互斥锁保护
thread_execution_times = []


def execute_rule_without_lock(rule):
    """
    执行单条规则，不申请设备锁，但依然记录开始、结束时间，用于统计线程执行时间。
    """
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    action_devices = rule["Action"]

    sleep(random.uniform(0, 20))


    start_time = time()
    sleep(random.uniform(1, 2))
    try:
        # 模拟规则执行（不加锁）
        print(f"Executing rule {ruleid}...")

        # # 更新全局状态字典（仅用 device_status_lock 来保护状态写操作）
        # with device_status_lock:
        #     if trigger_device[0] in device_status:
        #         device_status[trigger_device[0]] = trigger_device[1]
        #
        #     for action in action_devices:
        #         if action[0] in device_status:
        #             device_status[action[0]] = action[1]

        # 记录规则执行顺序
        execution_order.append(ruleid)

    finally:
        # 记录线程执行时间
        end_time = time()
        exec_time = end_time - start_time
        thread_execution_times.append(exec_time)


def execute_all_rules_concurrently_without_lock(rules):
    """
    并发执行所有规则（无锁），返回平均线程执行时间。
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

    # 输出当前轮所有线程的耗时列表（可选）
    print("execution times:", thread_execution_times)

    # 计算并返回每个线程的平均执行时长
    total_time = sum(thread_execution_times)
    count = len(thread_execution_times)
    avg_thread_time = (total_time / count) if count else 0.0

    return avg_thread_time


def find_conflict_reverse_pairs(execution_order):
    """
    检测 execution_order 中的冲突逆序对
    """
    conflict_dict = StatusMapping.find_rule_conflicts(RuleSet.get_all_rules())

    conflict_reverse_pairs = []
    n = len(execution_order)
    for i in range(n):
        for j in range(i + 1, n):
            rule_i = execution_order[i]
            rule_j = execution_order[j]
            if rule_j < rule_i:
                # 对于找到的逆序对，要以小的id作为key值，检查大的id是否影响了小的id的规则
                if rule_i in conflict_dict.get(rule_j, set()):
                    conflict_reverse_pairs.append((rule_i, rule_j))

    return conflict_reverse_pairs


def run_experiment():
    """
    在 LockOut 模式下，对 1~5 组规则各执行 20 轮实验，将每轮的执行时间列表写入文件。
    """
    base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockOut"

    for group_number in range(1, 6):
        group_rules = getattr(RuleSet, f"Group{group_number}")
        conflict_file = f"{base_path}\\num_lockout_group_{group_number}.txt"
        time_file = f"{base_path}\\time_lockout_group_{group_number}.txt"

        with open(conflict_file, "w") as conflict_output, open(time_file, "w") as time_output:
            for round_number in range(10):  # 每组执行20轮
                global device_status, execution_order, thread_execution_times
                # 重置全局变量
                device_status = {key: 0 for key in device_status}
                execution_order = []
                thread_execution_times = []

                # 并发执行所有规则(无锁)，并计算平均执行时间
                avg_thread_time = execute_all_rules_concurrently_without_lock(group_rules)

                # 找到冲突逆序对
                conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)
                conflict_count = len(conflict_reverse_pairs)

                # 写入冲突数量
                conflict_output.write(f"{conflict_count}\n")

                # 将本轮所有线程执行时间(逗号分隔)写入文件
                times_str = ",".join(f"{t:.4f}" for t in thread_execution_times)
                time_output.write(times_str + "\n")

                print(f"Group {group_number}, Round {round_number + 1}: "
                      f"{conflict_count} conflicts")


if __name__ == "__main__":
    run_experiment()
