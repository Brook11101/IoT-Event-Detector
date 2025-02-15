import copy
import threading
from time import time, sleep
import random
import ast
from Synchronizer.CV.UserScenario import get_user_scenario  # 用户定义的模板，用于比对预期顺序
from Synchronizer.CV.UserScenario import build_dependency_map  # 用户定义的模板，用于比对预期顺序
from RuleSet import deviceStatus
from Message import send_message
from Message import create_streams
from Message import clear_all_streams
from Message import consume_messages_from_offset



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
device_locks_fifo = {device: FIFOLock() for device in deviceStatus} # FIFO设备锁池，用于确保规则启动时预分配Trigger和Action设备锁时的顺序性
device_locks = {device: DeviceLock() for device in deviceStatus}  # 设备锁池

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


def execute_rule(rule, output_list, lock, dependency_map, offset_dict_global, offset_dict_cur, barrier, missing_rules,
                 llsc_list, time_list):
    """执行单条规则"""
    rule_id = rule["id"]
    rule_name = f"rule-{rule_id}"
    devices_to_lock = sorted(rule["TotalLock"])

    local_offset_dict = {}
    barrier.wait()
    rule_trigger_time = time()

    # **FIFO Lock 申请锁**
    events = {device: device_locks_fifo[device].async_acquire() for device in devices_to_lock}

    # **发送 `start` 消息**
    if rule.get("Condition"):
        condition_device = rule["Condition"][0]
        msg_id = send_message(rule_name, f"Stream_{condition_device}", "start", rule_id)
        if msg_id:
            local_offset_dict[f"Stream_{condition_device}"] = msg_id

    def acquire_and_send(device, event):
        while not device_locks_fifo[device].try_acquire(event):
            continue  # 轮询 `try_acquire()`
        msg_id = send_message(rule_name, f"Stream_{device}", "start", rule_id)
        if msg_id:
            local_offset_dict[f"Stream_{device}"] = msg_id
        device_locks_fifo[device].release()

    threads = [threading.Thread(target=acquire_and_send, args=(dev, ev)) for dev, ev in events.items()]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"[{rule_name}] 获取设备锁，开始等待依赖规则完成：{devices_to_lock}")

    # **监听依赖的 `end` 消息**
    waiting_threads = []
    results = []
    if rule_id in dependency_map:
        for device, wait_rules in dependency_map[rule_id].items():
            if wait_rules:
                def worker():
                    result = consume_messages_from_offset(rule_name, rule_id, f"Stream_{device}", wait_rules, offset_dict_cur, missing_rules)
                    results.append(result)

                thread = threading.Thread(target=worker)
                waiting_threads.append(thread)
                thread.start()

        for thread in waiting_threads:
            thread.join()

        if not all(results):
            print(f"规则 {rule_id} 依赖等待失败，停止执行")
            return

    # **执行任务**
    print(f"规则 {rule_id} 重新获取所有设备锁，开始执行...")
    sleep(random.uniform(1, 2))
    output_list.append(rule)

    # **发送 `end` 消息**
    for device in devices_to_lock:
        send_message(rule_name, f"Stream_{device}", "end", rule_id)

    if rule.get("Condition"):
        send_message(rule_name, f"Stream_{rule['Condition'][0]}", "end", rule_id)

    print(f"规则 {rule_id} 执行完成，已释放锁：{devices_to_lock}")
    time_list.append(time() - rule_trigger_time)

    with lock:
        offset_dict_global.update(local_offset_dict)
        print(f"规则 {rule_id} 更新 offset_dict: {local_offset_dict}")


def process_epoch(epoch_logs, output_logs, offset_dict_global, offset_dict_cur, missing_rules, llsc_list, time_list):
    """
    1. **创建 Barrier，确保所有规则线程同步启动**。
    2. **筛选 epoch_logs，移除 `ancestor` 在 `llsc_list` 里的规则**。
    3. **为每个规则创建线程，所有线程到达 Barrier 后同时开始**。
    4. **等待所有线程执行完毕**。
    """
    num_rules = len(epoch_logs)
    if num_rules == 0:
        return

    filtered_logs = []

    for log in epoch_logs:
        ancestor_id = log["ancestor"]

        if ancestor_id in llsc_list:
            llsc_list.append(log["id"])  # **如果 `ancestor` 失败，当前规则也应该加入 `llsc_list`**
            print(f"规则 {log['id']} 被跳过，因为其 `ancestor` 规则 {ancestor_id} 没有执行成功")
        else:
            filtered_logs.append(log)

    # **更新 Barrier 只控制真实执行的规则**
    barrier = threading.Barrier(len(filtered_logs))

    threads = []
    lock = threading.Lock()

    s1, s2 = get_user_scenario()
    dependency_map = build_dependency_map(s2)

    for log in filtered_logs:
        thread = threading.Thread(target=execute_rule, args=(
            log, output_logs, lock, dependency_map, offset_dict_global, offset_dict_cur, barrier, missing_rules,
            llsc_list, time_list))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # **确保当前轮次所有规则执行完，再执行下一个轮次**


def generate_cv_logs(input_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt",
                     output_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\cv_logs.txt"):
    """
    1. **读取 `static_logs.txt`**，获取规则数据。
    2. **对每个 `epoch_logs` 轮次，使用 `Barrier` 机制执行所有规则**。
    3. **将最终执行顺序存入 `cv_logs.txt`**，不同 `epoch` 之间插入空行区分。
    4. **返回 `missing_rules` 和 `llsc_list` 记录的执行失败规则**。
    """
    epochs_logs = read_static_logs(input_file)
    final_logs = []
    offset_dict_global = {}  # 维护全局偏移量
    offset_dict_cur = {}  # 每轮次更新
    missing_rules = []  # 记录缺失规则
    llsc_list = []  # **记录因为 LLSC 没有执行成功的规则**
    time_list = []

    for epoch_logs in epochs_logs:
        offset_dict_cur = copy.copy(offset_dict_global)
        process_epoch(epoch_logs, final_logs, offset_dict_global, offset_dict_cur, missing_rules, llsc_list, time_list)
        final_logs.append("")  # **插入空行，区分不同 epoch**

    with open(output_file, "w", encoding="utf-8") as f:
        for log in final_logs:
            f.write(str(log) + "\n")

    print(f"Simulation completed. Results saved to {output_file}")
    return missing_rules, llsc_list, time_list  # **返回 missing_rules 和 llsc_list , time_list**


### === 第二部分：检测 Race Condition === ###
def read_cv_logs(filename):
    """
    读取 `cv_logs.txt` 并解析成规则列表，保留执行顺序。
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # **按空行分割不同轮次**
    epochs = data.split("\n\n")
    epochs_logs = [[ast.literal_eval(line) for line in epoch.split("\n") if line.strip()] for epoch in epochs]

    return epochs_logs  # **返回每个轮次的日志列表**


def detectRaceCondition_per_epoch(epochs_logs):
    """
    **对每个轮次(epoch)单独执行Race Condition检测**，然后累积所有轮次的检测结果，返回总计的 Race Condition 统计。

    :param epochs_logs: 轮次划分的日志数据
    :return: 累积所有轮次的 `conflict_dict` (包含 AC, UC, CBK, CP)
    """
    cumulative_conflict_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}  # **存储所有轮次的累积 Race Condition 结果**
    logged_pairs = set()  # 记录已检测的 conflict pair，防止重复添加

    for epoch_logs in epochs_logs:  # **逐个轮次(epoch)执行Race Condition检测**
        for i in range(len(epoch_logs)):
            current_rule = epoch_logs[i]
            current_actions = current_rule["Action"]
            cur_rule_id = current_rule["id"]

            # **Condition Block (CBK)**
            if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
                cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):  # **只在当前轮次(epoch)内回溯**
                    former_rule = epoch_logs[j]
                    frm_rule_id = former_rule["id"]
                    for former_act in former_rule["Action"]:
                        if former_act[0] == cond_dev:
                            pair_cbk = (frm_rule_id, cur_rule_id)
                            if pair_cbk not in logged_pairs:
                                logged_pairs.add(pair_cbk)
                                cumulative_conflict_dict["CBK"].append(pair_cbk)
                            break
                    else:
                        continue
                    break

            # **Action Conflict / Unexpected Conflict**
            if current_rule['status'] == 'run':
                for j in range(i - 1, -1, -1):  # **只在当前轮次(epoch)内查找**
                    former_rule = epoch_logs[j]
                    frm_rule_id = former_rule["id"]

                    for latter_act in current_actions:
                        for former_act in former_rule["Action"]:
                            if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                                pair = (frm_rule_id, cur_rule_id)
                                if former_rule["ancestor"] == current_rule["ancestor"]:
                                    if pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        cumulative_conflict_dict["AC"].append(pair)
                                else:
                                    if pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        cumulative_conflict_dict["UC"].append(pair)

                # **Condition Pass (CP)**
                if current_rule.get('Condition'):
                    cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        former_rule = epoch_logs[j]
                        frm_rule_id = former_rule["id"]
                        if [cond_dev, cond_state] in former_rule["Action"]:
                            pair_cp = (frm_rule_id, cur_rule_id)
                            if pair_cp not in logged_pairs:
                                logged_pairs.add(pair_cp)
                                cumulative_conflict_dict["CP"].append(pair_cp)
                            break

    return cumulative_conflict_dict  # **返回所有轮次的 Race Condition 统计**


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


def WithCV_TALOCK():

    clear_all_streams()
    create_streams()

    # 生成 `cv_logs.txt` 并获取缺失规则
    missing_rules, llsc_list, time_list = generate_cv_logs()

    print(time_list)

    print("== 缺失规则 ==")
    print(missing_rules)

    print("== 未执行规则 ==")
    print(llsc_list)

    # 读取 `cv_logs.txt`
    cv_logs = read_cv_logs(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\cv_logs.txt")

    # 从 `cv_logs.txt` 检测 Race Condition
    conflict_dict = detectRaceCondition_per_epoch(cv_logs)

    # 获取用户定义的标准顺序
    user_template, user_template_dict = get_user_scenario()

    print("== 标准顺序 ==")
    print(build_dependency_map(user_template_dict))

    # 比较 `cv_conflict_dict` 和 `user_template`
    conflict_result, mismatch_count = check_rcs(user_template, conflict_dict)

    print(f"Before double check sequence conflict number: {mismatch_count}")

    # **去除 conflict_result 中出现在 missing_rules 里的冲突**
    filtered_conflict_result = {conflict_type: [] for conflict_type in conflict_result}

    for conflict_type, conflicts in conflict_result.items():
        for pair in conflicts:
            if pair not in missing_rules and (pair[1], pair[0]) not in missing_rules:
                filtered_conflict_result[conflict_type].append(pair)

    # **计算新的 mismatch_count**
    new_mismatch_count = sum(len(conflicts) for conflicts in filtered_conflict_result.values())

    # **输出最终结果**
    print("=== Final Check Conflict Results (Filtered) ===")
    print(f"Total Mismatched Conflicts: {new_mismatch_count}")
    print("Detailed Mismatched Conflicts:")
    for conflict_type, mismatches in filtered_conflict_result.items():
        print(f"{conflict_type}: {mismatches}")

    return filtered_conflict_result, new_mismatch_count, time_list


if __name__ == "__main__":
    WithCV_TALOCK()
