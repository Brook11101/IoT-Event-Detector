import threading
import time
import random
import ast
from Synchronizer.CV.UserTemplate import getUserTemplate  # 用户定义的模板，用于比对预期顺序
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

### === 第一部分：读取和生成 `nocv_logs.txt` === ###
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

def execute_rule(rule, output_list, lock):
    """
    执行单条规则：
    1. **按照 `Lock` 标签中的设备获取设备锁**。
    2. **按字典序排序，依次申请所有锁，确保获取顺序固定，避免死锁**。
    3. **成功获取所有锁后，执行任务（sleep 1-2s）**。
    4. **任务完成后，释放所有锁**。
    """

    # 需要获取的设备锁（来自 `Lock` 标签），按字典序排序
    devices_to_lock = sorted(rule["TotalLock"])

    # **按字典序申请所有设备锁**
    for device in devices_to_lock:
        device_locks[device].acquire()

    try:
        print(f"规则 {rule['id']} 已获取所有锁，开始执行...")
        time.sleep(random.uniform(1, 2))  # **模拟任务执行**
        output_list.append(rule)  # **线程安全地记录执行顺序**
    finally:
        # **按字典序释放所有设备锁**
        for device in devices_to_lock:
            device_locks[device].release()
        print(f"规则 {rule['id']} 执行完成，已释放锁：{devices_to_lock}")

def process_epoch(epoch_logs, output_logs):
    """
    并发执行单个轮次的所有规则，按实际完成顺序记录。
    """
    threads = []
    lock = threading.Lock()

    for log in epoch_logs:
        thread = threading.Thread(target=execute_rule, args=(log, output_logs, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # 确保当前轮次所有规则执行完，再执行下一个轮次

def generate_nocv_logs(input_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt", output_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\nocv_logs.txt"):
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
def read_nocv_logs(filename):
    """
    读取 `nocv_logs.txt` 并解析成规则列表，保留执行顺序。
    """
    with open(filename, "r", encoding="utf-8") as f:
        return [ast.literal_eval(line.strip()) for line in f]


# 除了考虑检测出来的顺序，还得考虑规则的启动顺序，先启动的规则不可见后启动的规则,故更新为只检测frm_rule_id>cur_rule_id的
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
        nocv_pairs = set(conflict_dict[conflict_type])

        for pair in nocv_pairs:
            reversed_pair = (pair[1], pair[0])
            if reversed_pair in expected_pairs:  # 顺序发生颠倒
                check_result[conflict_type].append(pair)
                mismatch_count += 1

    return check_result, mismatch_count

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


def main():
    # 生成 `nocv_logs.txt`
    generate_nocv_logs()

    # 读取 `nocv_logs.txt`
    nocv_logs = read_nocv_logs(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\nocv_logs.txt")

    # 从 `nocv_logs.txt` 检测 Race Condition
    conflict_dict = detectRaceCondition(nocv_logs)

    # **获取所有规则的 Score**
    rule_scores = {rule["id"]: rule["score"] for rule in nocv_logs}  # 提取 score 映射

    # # 获取用户定义的标准顺序
    # user_template,user_template_device = getUserTemplate()
    # # 比较 `nocv_conflict_dict` 和 `user_template`
    # conflict_result, mismatch_count = check_rcs(user_template, conflict_dict)

    # **使用 score 计算 Race Condition，并分类统计**
    conflict_result, mismatch_count = check_racecondition_with_score(conflict_dict, rule_scores)

    # **分类打印输出**
    print("=== Final Check Conflict Results ===")
    print(f"Total Mismatched Conflicts: {mismatch_count}")
    print("Detailed Mismatched Conflicts:")
    for conflict_type, mismatches in conflict_result.items():
        print(f"{conflict_type}: {mismatches}")

    return conflict_result, mismatch_count

if __name__ == "__main__":
    main()
