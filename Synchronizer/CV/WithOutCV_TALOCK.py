import threading
import time
import random
import ast
from Synchronizer.CV.UserScenario import get_user_scenario  # 用户定义的模板，用于比对预期顺序
from RuleSet import deviceStatus

deviceStatus = deviceStatus

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
device_locks = {device: DeviceLock() for device in deviceStatus}  # 设备锁池

### === 第一部分：读取和生成 `nocv_lock_logs.txt` === ###
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

# **执行单个规则**
def execute_rule(rule, output_list, lock, barrier):
    """
    规则执行：
    1. **先等待 `barrier`，保证所有线程同步启动**。
    2. **获取设备锁，确保锁顺序固定，避免死锁**。
    3. **执行任务**。
    4. **释放锁**。
    """
    rule_id = rule["id"]
    devices_to_lock = sorted(rule["TotalLock"])  # **按照字典序排序**

    # **等待所有线程到达屏障**
    barrier.wait()

    time.sleep(random.uniform(1, 2))  # **模拟触发到执行的延迟**

    # **按字典序申请所有设备锁**
    for device in devices_to_lock:
        device_locks[device].acquire()

    try:
        print(f"规则 {rule_id} 已获取所有锁，开始执行...")
        output_list.append(rule)  # **线程安全地记录执行顺序**
    finally:
        # **按字典序释放设备锁**
        for device in devices_to_lock:
            device_locks[device].release()
        print(f"规则 {rule_id} 执行完成，已释放锁：{devices_to_lock}")

# **并发执行当前轮次的所有规则**
def process_epoch(epoch_logs, output_logs):
    """
    1. **创建 `Barrier`，确保所有规则线程同步启动**。
    2. **为每个规则创建线程，所有线程到达 `Barrier` 后同时开始**。
    3. **等待所有线程执行完毕**。
    """
    num_rules = len(epoch_logs)
    if num_rules == 0:
        return

    # **创建 Barrier**
    barrier = threading.Barrier(num_rules)

    threads = []
    lock = threading.Lock()

    # **创建线程**
    for log in epoch_logs:
        thread = threading.Thread(target=execute_rule, args=(log, output_logs, lock, barrier))
        threads.append(thread)
        thread.start()

    # **等待所有线程执行完毕**
    for thread in threads:
        thread.join()


def generate_nocv_logs(input_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt",
                        output_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\nocv_lock_logs.txt"):
    """
    1. **读取 `static_logs.txt`**，获取规则数据。
    2. **对每个 `epoch_logs` 轮次，使用 `Barrier` 机制执行所有规则**。
    3. **将最终执行顺序存入 `nocv_lock_logs.txt`**，不同 `epoch` 之间插入空行区分。
    """
    epochs_logs = read_static_logs(input_file)  # 读取日志数据
    final_logs = []  # 存储执行顺序

    for epoch_logs in epochs_logs:
        process_epoch(epoch_logs, final_logs)
        final_logs.append("")  # **插入空行，区分不同 epoch**

    # **写入 `nocv_lock_logs.txt`**
    with open(output_file, "w", encoding="utf-8") as f:
        for log in final_logs:
            f.write(str(log) + "\n")

    print(f"Simulation completed. Results saved to {output_file}")

### === 第二部分：检测 Race Condition === ###

# def read_nocv_logs(filename):
#     """
#     读取 `nocv_lock_logs.txt` 并解析成规则列表，保留执行顺序。
#     """
#     with open(filename, "r", encoding="utf-8") as f:
#         return [ast.literal_eval(line.strip()) for line in f]
#
#
# # 基于日志全局检测潜在的所有race condition的逻辑
# def detectRaceCondition(logs):
#     """
#     复用 `detectRaceCondition` 逻辑，检测 `cv_logs.txt` 里面的 AC、UC、CP、CBK。
#     """
#     conflict_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}
#     logged_pairs = set()  # 记录已检测的 conflict pair
#
#     for i in range(len(logs)):
#         current_rule = logs[i]
#         current_actions = current_rule["Action"]
#         cur_rule_id = current_rule["id"]
#
#         # Condition Block (CBK)
#         if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
#             cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
#             for j in range(i - 1, -1, -1):
#                 former_rule = logs[j]
#                 frm_rule_id = former_rule["id"]
#                 for former_act in former_rule["Action"]:
#                     if former_act[0] == cond_dev:
#                         pair_cbk = (frm_rule_id, cur_rule_id)
#                         if pair_cbk not in logged_pairs:
#                             logged_pairs.add(pair_cbk)
#                             conflict_dict["CBK"].append(pair_cbk)
#                         break
#                 else:
#                     continue
#                 break
#
#         # 其他 Race Condition 只在 `run` 规则里检测
#         if current_rule['status'] == 'run':
#             # Action Conflict / Unexpected Conflict
#             for j in range(i - 1, -1, -1):
#                 former_rule = logs[j]
#                 frm_rule_id = former_rule["id"]
#
#                 for latter_act in current_actions:
#                     for former_act in former_rule["Action"]:
#                         if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
#                             pair = (frm_rule_id, cur_rule_id)
#                             if former_rule["ancestor"] == current_rule["ancestor"]:
#                                 if pair not in logged_pairs:
#                                     logged_pairs.add(pair)
#                                     conflict_dict["AC"].append(pair)
#                             else:
#                                 if pair not in logged_pairs:
#                                     logged_pairs.add(pair)
#                                     conflict_dict["UC"].append(pair)
#
#             # Condition Pass (CP)
#             if current_rule.get('Condition'):
#                 cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
#                 for j in range(i - 1, -1, -1):
#                     former_rule = logs[j]
#                     frm_rule_id = former_rule["id"]
#                     if [cond_dev, cond_state] in former_rule["Action"]:
#                         pair_cp = (frm_rule_id, cur_rule_id)
#                         if pair_cp not in logged_pairs:
#                             logged_pairs.add(pair_cp)
#                             conflict_dict["CP"].append(pair_cp)
#                         break
#
#     return conflict_dict

def read_nocv_logs(filename):
    """
    读取 `nocv_lock_logs.txt` 并解析成规则列表，按轮次(epoch)返回。
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # **按空行分割不同轮次**
    epochs = data.split("\n\n")
    epochs_logs = [[ast.literal_eval(line) for line in epoch.split("\n") if line.strip()] for epoch in epochs]

    return epochs_logs  # **返回每个轮次的日志列表**

# 按照轮次划分过滤潜在CRI，得到真实CRI
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
        nocv_pairs = set(conflict_dict[conflict_type])

        for pair in nocv_pairs:
            reversed_pair = (pair[1], pair[0])
            if reversed_pair in expected_pairs:  # 顺序发生颠倒
                check_result[conflict_type].append(pair)
                mismatch_count += 1
    return check_result, mismatch_count

# 基于score筛选出不符合用户真实意愿的CRI
def check_racecondition_with_score(conflict_dict, rule_scores):
    """
    计算 Race Condition，按照类别 (AC, UC, CBK, CP) 统计：
    - 遍历 conflict_dict 中的所有 (a, b) 对。
    - 如果 score(a) < score(b)，表示 b 本应先执行，但 a 先执行了，这是一个 Race Condition。
    - 统计并返回更新后的 conflict_dict 和 总计不合理的冲突数量 mismatch_count。

    :param conflict_dict: 包含 AC、UC、CBK、CP 类型的 conflict 对象
    :param rule_scores: 规则 ID -> Score 的映射 {rule_id: score}
    :return: (更新后的 conflict_dict, mismatch_count)
    """
    updated_conflict_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}
    mismatch_count = 0  # 统计 Race Condition 总数

    for conflict_type, pairs in conflict_dict.items():
        for (a, b) in pairs:
            score_a = rule_scores.get(a, float("inf"))  # 获取 a 的 score，默认为无穷大
            score_b = rule_scores.get(b, float("inf"))  # 获取 b 的 score，默认为无穷大

            if score_a < score_b:  # 发现 a 应该在 b 之后执行，但 a 先执行了
                updated_conflict_dict[conflict_type].append((a, b))
                mismatch_count += 1  # 统计不合理的冲突数量
    return updated_conflict_dict, mismatch_count


def WithOutCV_TALOCK():
    # 生成 `nocv_lock_logs.txt`
    generate_nocv_logs()

    # 读取 `nocv_lock_logs.txt`
    nocv_logs = read_nocv_logs(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\nocv_lock_logs.txt")

    # 从 `nocv_logs.txt` 检测真实 Race Condition
    conflict_dict = detectRaceCondition_per_epoch(nocv_logs)

    conflict_result = conflict_dict
    mismatch_count = len(conflict_dict["AC"]) + len(conflict_dict["UC"]) + len(conflict_dict["CBK"]) + len(conflict_dict["CP"])

    # # **获取所有规则的 Score**
    # rule_scores = {rule["id"]: rule["score"] for epoch in nocv_logs for rule in epoch}
    # # **使用 score 计算 Race Condition，并分类统计**
    # # 从真实CRI检测不合用户预期CRI
    # conflict_result, mismatch_count = check_racecondition_with_score(conflict_dict, rule_scores)

    # **分类打印输出**
    print("=== Final Check Conflict Results ===")
    print(f"Total Mismatched Conflicts: {mismatch_count}")
    print("Detailed Mismatched Conflicts:")
    for conflict_type, mismatches in conflict_result.items():
        print(f"{conflict_type}: {mismatches}")

    return conflict_result, mismatch_count

if __name__ == "__main__":
    WithOutCV_TALOCK()
