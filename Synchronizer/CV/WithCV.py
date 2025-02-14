import copy
import threading
from time import time,sleep
import random
import ast
from Synchronizer.CV.LLSC import clear_table, insert_log
from Synchronizer.CV.UserScenario import get_user_scenario  # 用户定义的模板，用于比对预期顺序
from Synchronizer.CV.UserScenario import build_dependency_map  # 用户定义的模板，用于比对预期顺序
from RuleSet import deviceStatus
from Message import send_message, send_message_atomic
from Message import create_streams
from Message import clear_all_streams
from Message import consume_messages_from_offset


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


def execute_rule(rule, output_list, lock, dependency_map, offset_dict_global, offset_dict_cur, barrier, missing_rules):
    """
    执行单条规则：
    1. **获取设备锁/使用LLSC，发送 `start` 消息**。
    2. **释放锁，监听 `end` 消息，等待所有依赖的规则完成**。
    3. **依赖满足后，重新获取设备锁，执行任务**。
    4. **执行完成后，发送 `end` 消息，并释放设备锁**。
    """

    rule_id = rule["id"]
    rule_name = f"rule-{rule_id}"
    # 1️ **获取设备锁**
    devices_to_lock = sorted(rule["Lock"])  # **按照字典序获取所有锁**
    local_offset_dict = {}  # 本地偏移量记录，用于更新全局 offset_dict

    # 2 收集所有要发送的 stream
    stream_list = []

    # 如果规则有 Condition，不为空，则给 Condition 设备也发送 "start"
    if rule.get("Condition"):
        condition_device = rule["Condition"][0]  # 获取 Condition 设备
        stream_list.append(f"Stream_{condition_device}")

    # 处理规则涉及的设备
    for device in devices_to_lock:
        stream_list.append(f"Stream_{device}")

    # **等待所有线程到达屏障**
    barrier.wait()

    rule_trigger_time = time()

    sleep(random.uniform(1, 2))  # **模拟触发到执行的延迟**

    print(f"[{rule_name}] 收到Action，开始执行，需要设备：{devices_to_lock}")

    # 3. 调用 `send_message_atomic()` 进行**原子性**发送
    if stream_list:
        offset_dict = send_message_atomic(rule_name, stream_list, "start", rule_id)
        if offset_dict:
            local_offset_dict.update(offset_dict)  # 直接合并返回的偏移量字典

    # 4️ **监听依赖的 `end` 消息**
    waiting_threads = []
    results = []  # 存储所有线程的返回值

    if rule_id in dependency_map:
        for device, wait_rules in dependency_map[rule_id].items():
            if wait_rules:  # 仅在有依赖规则时监听
                stream_name = f"Stream_{device}"

                def worker():
                    result = consume_messages_from_offset(rule_name, rule_id, stream_name, wait_rules, offset_dict_cur,
                                                          missing_rules)
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
            print(f"规则 {rule_id} 依赖等待失败,停止执行")
            return

    try:
        # 6️ **执行任务**

        print(f"规则 {rule_id} 已获取所有设备锁，开始执行...")

        # 使用LLSC机制，插入记录
        cur_time = time

        insert_log(rule["RuleId"], rule_id, rule_trigger_time)

        output_list.append(rule)  # **记录执行顺序**

        # 7️ **发送 `end` 消息**
        if stream_list:
            for stream in stream_list:
                send_message(rule_name, stream, "end", rule_id)

    finally:
        # 8️ **释放设备锁**
        print(f"规则 {rule_id} 执行完成，已释放锁：{devices_to_lock}")

        with lock:
            offset_dict_global.update(local_offset_dict)
            print(f"规则 {rule_id} 更新 offset_dict: {local_offset_dict}")


def process_epoch(epoch_logs, output_logs, offset_dict_global, offset_dict_cur, missing_rules):
    """
    1. **创建 Barrier，确保所有规则线程同步启动**。
    2. **为每个规则创建线程，所有线程到达 Barrier 后同时开始**。
    3. **等待所有线程执行完毕**。
    """
    num_rules = len(epoch_logs)
    if num_rules == 0:
        return

    # **创建 Barrier**
    barrier = threading.Barrier(num_rules)

    threads = []
    lock = threading.Lock()

    s1, s2 = get_user_scenario()
    dependency_map = build_dependency_map(s2)

    for log in epoch_logs:
        thread = threading.Thread(target=execute_rule, args=(
            log, output_logs, lock, dependency_map, offset_dict_global, offset_dict_cur, barrier, missing_rules))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # 确保当前轮次所有规则执行完，再执行下一个轮次


def generate_cv_logs(input_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt",
                     output_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\cv_logs.txt"):
    """
    1. **读取 `static_logs.txt`**，获取规则数据。
    2. **对每个 `epoch_logs` 轮次，使用 `Barrier` 机制执行所有规则**。
    3. **将最终执行顺序存入 `cv_logs.txt`**，不同 `epoch` 之间插入空行区分。
    4. **返回 missing_rules，记录哪些规则本应该出现但没有出现。**
    """
    epochs_logs = read_static_logs(input_file)
    final_logs = []
    offset_dict_global = {}  # 维护每个 Stream 的消费起始偏移量
    offset_dict_cur = {}  # 维护每个 Stream 的消费起始偏移量，但是每一轮次才更新使用一次
    missing_rules = []  # **收集所有轮次的 missing_rules**

    for epoch_logs in epochs_logs:
        offset_dict_cur = copy.copy(offset_dict_global)
        process_epoch(epoch_logs, final_logs, offset_dict_global, offset_dict_cur, missing_rules)
        final_logs.append("")  # **插入空行，区分不同 epoch**

    # 记录最终执行顺序
    with open(output_file, "w", encoding="utf-8") as f:
        for log in final_logs:
            f.write(str(log) + "\n")

    print(f"Simulation completed. Results saved to {output_file}")
    return missing_rules  # **返回 missing_rules**


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


def WithCV():

    clear_table()

    clear_all_streams()
    create_streams()

    # 生成 `cv_logs.txt` 并获取缺失规则
    missing_rules = generate_cv_logs()

    print("== 缺失规则 ==")
    print(missing_rules)

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

    return filtered_conflict_result, new_mismatch_count


if __name__ == "__main__":
    WithCV()
