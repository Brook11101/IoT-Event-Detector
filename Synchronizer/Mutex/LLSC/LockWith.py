import random
import threading
from time import sleep, time
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
        异步申请锁：返回一个 event，后续 try_acquire(event) 判断自己是否获取到锁。
        """
        event = threading.Event()
        with self.lock:
            self.queue.append(event)
            self.condition.notify_all()
        return event

    def try_acquire(self, event):
        """
        如果自己在队首且锁无人持有，则获取锁并返回 True，否则返回 False。
        """
        with self.lock:
            if self.queue and self.queue[0] == event and self.owner is None:
                self.owner = event
                self.queue.pop(0)
                return True
        return False

    def release(self):
        """
        释放锁，清除当前 owner 并唤醒其他等待线程。
        """
        with self.lock:
            self.owner = None
            self.condition.notify_all()


# -------------------
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
device_status_lock = threading.Lock()  # 用于保护 device_status 并发修改

# 记录规则执行的顺序
execution_order = []

# 全局设备锁字典
device_locks = {device: FIFOLock() for device in device_status}
# 用于在每次规则提交申请锁时，保证申请时的原子性
lock_acquire_guard = threading.Lock()

# 用于记录本轮每个线程执行时间
thread_execution_times = []
thread_execution_times_lock = threading.Lock()


def execute_rule(rule):
    """
    执行单条规则的线程函数。其主要流程：
      1. 记录开始时间。
      2. 依次申请所有所需的设备锁并获取。
      3. 执行规则：更新 device_status, 随机 sleep, 记录执行顺序等。
      4. 释放已获取的锁。
      5. 记录结束时间，并将本线程的耗时写入共享列表。
    """
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    action_devices = rule["Action"]
    condition_devices = rule.get("Condition", [])  # 条件设备(可选)

    # 1) 选出要获取锁的设备，并按字典序排序，避免死锁
    locks_to_acquire = sorted(
        [device for device in [trigger_device[0]]
         + ([condition_devices[0]] if condition_devices else [])
         + [action[0] for action in action_devices] if device in device_status]
    )

    start_time = time()
    # 2) 提交锁申请阶段
    events = {}
    with lock_acquire_guard:
        for device in locks_to_acquire:
            if device in device_locks:
                events[device] = device_locks[device].async_acquire()

    # 3) 轮询尝试获取锁，直到全部获取成功
    acquired_locks = set()
    while True:
        for device, event in events.items():
            if device not in acquired_locks and device_locks[device].try_acquire(event):
                acquired_locks.add(device)
        if len(acquired_locks) == len(locks_to_acquire):
            break

    try:
        # 模拟执行
        sleep(random.uniform(1, 2))

        # 更新全局状态
        with device_status_lock:
            # 更新 trigger_device 状态
            if trigger_device[0] in device_status:
                device_status[trigger_device[0]] = trigger_device[1]

            # 更新 action_devices 状态
            for action in action_devices:
                if action[0] in device_status:
                    device_status[action[0]] = action[1]

            print(f"Executing rule {ruleid}...")

            execution_order.append(ruleid)
            end_time = time()

    finally:
        # 4) 释放锁
        for device in acquired_locks:
            device_locks[device].release()

        # 5) 记录线程执行时间
        exec_time = end_time - start_time
        with thread_execution_times_lock:
            thread_execution_times.append(exec_time)


def execute_all_rules_concurrently(rules):
    """
    并发执行所有规则，并返回所有线程执行时间的平均值(avg_thread_time)。
    """
    threads = []

    for rule in rules:
        thread = threading.Thread(target=execute_rule, args=(rule,))
        threads.append(thread)
        thread.start()

    # 等待所有线程结束
    for thread in threads:
        thread.join()

    # 输出当前轮所有线程的耗时列表（可选）
    print("execution times:", thread_execution_times)

    # 计算并返回每个线程的平均执行时长
    with thread_execution_times_lock:
        total_time = sum(thread_execution_times)
        count = len(thread_execution_times)
    avg_thread_time = (total_time / count) if count else 0.0

    return avg_thread_time


def find_conflict_reverse_pairs(order):
    """
    检测 execution_order 中的冲突逆序对。
    """
    conflict_dict = StatusMapping.find_rule_conflicts(RuleSet.get_all_rules())

    conflict_reverse_pairs = []
    n = len(order)
    for i in range(n):
        for j in range(i + 1, n):
            rule_i = order[i]
            rule_j = order[j]
            if rule_j < rule_i:
                if rule_i in conflict_dict.get(rule_j, set()):
                    conflict_reverse_pairs.append((rule_i, rule_j))
    return conflict_reverse_pairs


def run_experiment():
    """
    对 1~5 组规则各执行 20 轮实验。
    - conflict_file   -> 每轮的冲突数量
    - time_file       -> 每轮的平均线程执行时间
    - detail_file     -> 每轮的全部线程执行时间列表（用于后续分析/绘图）
    """
    base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockWith"

    for group_number in range(1, 6):
        group_rules = getattr(RuleSet, f"Group{group_number}")
        conflict_file = f"{base_path}\\num_lockwith_group_{group_number}.txt"
        time_file = f"{base_path}\\time_lockwith_group_{group_number}.txt"

        with open(conflict_file, "w") as conflict_output, \
             open(time_file, "w") as time_output:

            for round_number in range(10):
                # ----重置全局变量----
                global device_status, execution_order, thread_execution_times
                device_status = {key: 0 for key in device_status}
                execution_order = []
                thread_execution_times = []

                # ----执行规则并计算平均线程执行时间----
                avg_thread_time = execute_all_rules_concurrently(group_rules)

                # ----统计冲突对----
                conflict_reverse_pairs = find_conflict_reverse_pairs(execution_order)
                conflict_count = len(conflict_reverse_pairs)

                # ----把冲突数量写入对应文件----
                conflict_output.write(f"{conflict_count}\n")

                # 你可以用逗号/空格分隔，也可以写成 JSON 格式，总之能被后续解析即可
                times_str = ",".join(f"{t:.4f}" for t in thread_execution_times)
                time_output.write(times_str + "\n")

                print(f"Group {group_number}, Round {round_number + 1}: "
                      f"{conflict_count} conflicts")


if __name__ == "__main__":
    run_experiment()
