import threading
import time
import random
import ast
from Synchronizer.CV.UserTemplate import getUserTemplate  # 用户定义的模板，用于比对预期顺序
from RuleSet import deviceStatus
from Message import send_message
from Message import create_streams
from Message import clear_all_streams
from Message import consume_messages_from_offset


def build_dependency_map(sorted_rc_dict_with_device):
    """
    根据 `sorted_rc_dict_with_device` 构建规则 ID 之间的依赖关系，按照设备 (deviceName) 组织。

    依赖字典结构:
    {
        rule_id: {
            deviceName1: {依赖的规则ID集合},
            deviceName2: {依赖的规则ID集合},
            ...
        },
        ...
    }

    仅当规则 ID 需要等待其他规则时，才会记录在字典里。
    """

    dependency_map = {}

    # **遍历所有 Race Condition 记录**
    for conflict_type, pairs_with_device in sorted_rc_dict_with_device.items():
        for (wait_id, current_id), device in pairs_with_device:
            # **初始化 `current_id` 在 dependency_map 里的结构**
            if current_id not in dependency_map:
                dependency_map[current_id] = {}

            # **初始化 `device` 在 `current_id` 里的集合**
            if device not in dependency_map[current_id]:
                dependency_map[current_id][device] = set()

            # **记录 `current_id` 需要等待的规则 `wait_id`**
            dependency_map[current_id][device].add(wait_id)

    return dependency_map

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


class DeviceLock:
    """
    设备锁管理类：管理单个设备的锁，支持持续尝试获取锁。
    """
    def __init__(self):
        self.lock = threading.Lock()  # 每个设备对应一个锁

    def acquire(self):
        """
        持续尝试获取锁，直到成功为止。
        """
        while True:
            if self.lock.acquire(blocking=False):  # 尝试获取锁
                return  # 成功获取锁，返回
            # 失败则继续循环，直到获取成功

    def release(self):
        """
        释放设备锁
        """
        self.lock.release()

# === 创建全局设备锁字典 ===
deviceStatus = deviceStatus
device_locks = {device: DeviceLock() for device in deviceStatus}  # 设备锁池
device_locks_fifo = {device: FIFOLock() for device in deviceStatus}

### === 第一部分：读取和生成 `cv_logs.txt` === ###
def read_static_logs(filename):
    """
    读取 `static_logs.txt`，按轮次 (epoch) 存储规则日志。
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # 按空行分割不同轮次
    epochs = data.split("\n\n")
    logs_per_epoch = [[ast.literal_eval(line) for line in epoch.split("\n") if line.strip()] for epoch in epochs]

    return logs_per_epoch


def execute_rule(rule, output_list, lock, dependency_map):
    """
    执行单条规则：
    1. **获取设备锁，并发送 `start` 消息**。
    2. **释放锁，监听 `end` 消息，等待所有依赖的规则完成**。
    3. **依赖满足后，重新获取设备锁，执行任务**。
    4. **执行完成后，发送 `end` 消息，并释放设备锁**。
    """

    rule_id = rule["id"]
    rule_name = f"rule-{rule_id}"

    # 1️ **获取设备锁**
    devices_to_lock = sorted(rule["Lock"])  # **按照字典序获取所有锁**

    # 1️⃣ **FIFO Lock: 申请锁，记录申请顺序**
    events = {}  # 存储每个设备的 `FIFOLock` 事件
    with lock:  # 确保 FIFO 申请的原子性
        for device in devices_to_lock :
            events[device] = device_locks_fifo[device].async_acquire()

    #  **如果规则有 Condition，不为空，则给 Condition 设备也发送 start**
    if rule.get("Condition"):
        condition_device = rule["Condition"][0]  # 获取 Condition 设备
        stream_name = f"Stream_{condition_device}"
        send_message(rule_name, stream_name, "start", rule_id)

    def acquire_and_send(device, event):
        while not device_locks_fifo[device].try_acquire(event):
            continue# 轮询 `try_acquire()`
        stream_name = f"Stream_{device}"
        send_message(rule_name, stream_name, "start", rule_id)
        device_locks_fifo[device].release()  # 发送完 `start` 立即释放锁

    threads = [threading.Thread(target=acquire_and_send, args=(dev, ev)) for dev, ev in events.items()]
    for t in threads: t.start()
    for t in threads: t.join()  # 等待所有 `start` 发送完毕


    # 4️ **监听依赖的 `end` 消息**
    waiting_threads = []
    results = []  # 存储所有线程的返回值

    if rule_id in dependency_map:
        for device, wait_rules in dependency_map[rule_id].items():
            if wait_rules:  # 仅在有依赖规则时监听
                stream_name = f"Stream_{device}"

                def worker():
                    result = consume_messages_from_offset(rule_name, rule_id, stream_name, wait_rules, '0-0')
                    results.append(result)  # 存储线程返回值

                thread = threading.Thread(target=worker)
                waiting_threads.append(thread)
                thread.start()

        # **等待所有监听线程完成**
        for thread in waiting_threads:
            thread.join()

        # **检查所有监听结果**
        if all(results):
            print(f"规则 {rule_id} 依赖等待成功")
        else:
            print(f"规则 {rule_id} 依赖等待失败")

    # 5️ **重新获取设备锁**
    for device in devices_to_lock:
        device_locks[device].acquire()

    try:
        # 6️ **执行任务**
        print(f"规则 {rule_id} 已获取所有锁，开始执行...")
        time.sleep(random.uniform(1, 2))  # **模拟任务执行**
        output_list.append(rule)  # **记录执行顺序**

        # 7️ **发送 `end` 消息**
        for device in devices_to_lock:
            stream_name = f"Stream_{device}"
            send_message(rule_name, stream_name, "end", rule_id)

        # **如果规则有 Condition，不为空，则给 Condition 设备也发送 end**
        if rule.get("Condition"):
            condition_device = rule["Condition"][0]
            stream_name = f"Stream_{condition_device}"
            send_message(rule_name, stream_name, "end", rule_id)

    finally:
        # 8️ **释放设备锁**
        for device in devices_to_lock:
            device_locks[device].release()
        print(f"规则 {rule_id} 执行完成，已释放锁：{devices_to_lock}")


def process_epoch(epoch_logs, output_logs):
    """
    并发执行单个轮次的所有规则，按实际完成顺序记录。
    """
    threads = []
    lock = threading.Lock()

    s1, s2 = getUserTemplate()
    dependency_map = build_dependency_map(s2)

    for log in epoch_logs:
        thread = threading.Thread(target=execute_rule, args=(log, output_logs, lock, dependency_map))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # 确保当前轮次所有规则执行完，再执行下一个轮次

def generate_cv_logs(input_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt", output_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\cv_logs.txt"):
    """
    读取 `static_logs.txt`，模拟无条件变量情况下的随机执行，并存入 `nocv_logs.txt`。
    """
    epochs_logs = read_static_logs(input_file)
    final_logs = []

    for epoch_logs in epochs_logs:
        process_epoch(epoch_logs, final_logs)

    # 记录最终执行顺序
    with open(output_file, "w", encoding="utf-8") as f:
        for log in final_logs:
            f.write(str(log) + "\n")

    print(f"Simulation completed. Results saved to {output_file}")

### === 第二部分：检测 Race Condition === ###
def read_cv_logs(filename):
    """
    读取 `cv_logs.txt` 并解析成规则列表，保留执行顺序。
    """
    with open(filename, "r", encoding="utf-8") as f:
        return [ast.literal_eval(line.strip()) for line in f]

def detectRaceCondition(logs):
    """
    复用 `detectRaceCondition` 逻辑，检测 `cv_logs.txt` 里面的 AC、UC、CP、CBK。
    """
    conflict_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}
    logged_pairs = set()  # 记录已检测的 conflict pair

    for i in range(len(logs)):
        current_rule = logs[i]
        current_actions = current_rule["Action"]
        cur_rule_id = current_rule["id"]

        # Condition Block (CBK)
        if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
            cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
            for j in range(i - 1, -1, -1):
                former_rule = logs[j]
                frm_rule_id = former_rule["id"]
                for former_act in former_rule["Action"]:
                    if former_act[0] == cond_dev:
                        pair_cbk = (frm_rule_id, cur_rule_id)
                        if frm_rule_id>cur_rule_id and pair_cbk not in logged_pairs:
                            logged_pairs.add(pair_cbk)
                            conflict_dict["CBK"].append(pair_cbk)
                        break
                else:
                    continue
                break

        # 其他 Race Condition 只在 `run` 规则里检测
        if current_rule['status'] == 'run':
            # Action Conflict / Unexpected Conflict
            for j in range(i - 1, -1, -1):
                former_rule = logs[j]
                frm_rule_id = former_rule["id"]

                for latter_act in current_actions:
                    for former_act in former_rule["Action"]:
                        if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                            pair = (frm_rule_id, cur_rule_id)
                            if former_rule["ancestor"] == current_rule["ancestor"]:
                                if frm_rule_id>cur_rule_id and pair not in logged_pairs:
                                    logged_pairs.add(pair)
                                    conflict_dict["AC"].append(pair)
                            else:
                                if frm_rule_id>cur_rule_id and pair not in logged_pairs:
                                    logged_pairs.add(pair)
                                    conflict_dict["UC"].append(pair)

            # Condition Pass (CP)
            if current_rule.get('Condition'):
                cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):
                    former_rule = logs[j]
                    frm_rule_id = former_rule["id"]
                    if [cond_dev, cond_state] in former_rule["Action"]:
                        pair_cp = (frm_rule_id, cur_rule_id)
                        if frm_rule_id>cur_rule_id and pair_cp not in logged_pairs:
                            logged_pairs.add(pair_cp)
                            conflict_dict["CP"].append(pair_cp)
                        break

    return conflict_dict

### === 第三部分：比对用户预期顺序 === ###
def check_rcs(user_template_dict, conflict_dict):
    check_result = {"AC": [], "UC": [], "CBK": [], "CP": []}
    mismatch_count = 0  # 统计顺序不一致的冲突数量

    for conflict_type in user_template_dict:
        expected_pairs = set(user_template_dict[conflict_type])
        cv_pairs = set(conflict_dict[conflict_type])

        for pair in cv_pairs:
            reversed_pair = (pair[1], pair[0])
            if reversed_pair in expected_pairs:  # 顺序发生颠倒
                check_result[conflict_type].append(pair)
                mismatch_count += 1

    return check_result, mismatch_count

def main():

    clear_all_streams()

    create_streams()

    # 生成 `cv_logs.txt`
    generate_cv_logs()

    # 读取 `cv_logs.txt`
    cv_logs = read_cv_logs(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\cv_logs.txt")

    # 从 `cv_logs.txt` 检测 Race Condition
    conflict_dict = detectRaceCondition(cv_logs)

    # 获取用户定义的标准顺序
    user_template,user_template_dict = getUserTemplate()

    # 比较 `cv_conflict_dict` 和 `user_template`
    conflict_result, mismatch_count = check_rcs(user_template, conflict_dict)

    # 输出最终结果
    print("=== Final Check Conflict Results ===")
    print(f"Total Mismatched Conflicts: {mismatch_count}")
    print("Detailed Mismatched Conflicts:")
    for conflict_type, mismatches in conflict_result.items():
        print(f"{conflict_type}: {mismatches}")

    return conflict_result, mismatch_count

if __name__ == "__main__":
    main()