import ast


def detectRaceCondition_per_epoch(epochs_logs):
    """
    **对每个轮次(epoch)单独执行 Race Condition 检测，并记录冲突设备**。

    :param epochs_logs: 轮次划分的日志数据
    :return: (rc_dict, rc_dict_with_device)
             rc_dict:      { "AC": [...], "UC": [...], "CBK": [...], "CP": [...] }
             rc_dict_with_device:  { "AC": [...], "UC": [...], "CBK": [...], "CP": [...] }
    """

    rc_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}  # **存储所有轮次的 Race Condition 结果**
    rc_dict_with_device = {"AC": [], "UC": [], "CBK": [], "CP": []}  # **存储冲突设备信息**
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
                            conflict_device = former_act[0]  # **冲突设备**
                            if pair_cbk not in logged_pairs:
                                logged_pairs.add(pair_cbk)
                                rc_dict["CBK"].append(pair_cbk)
                                rc_dict_with_device["CBK"].append((pair_cbk, conflict_device))
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
                                conflict_device = latter_act[0]  # **冲突设备**
                                if former_rule["ancestor"] == current_rule["ancestor"]:
                                    if pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        rc_dict["AC"].append(pair)
                                        rc_dict_with_device["AC"].append((pair, conflict_device))
                                else:
                                    if pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        rc_dict["UC"].append(pair)
                                        rc_dict_with_device["UC"].append((pair, conflict_device))

                # **Condition Pass (CP)**
                if current_rule.get('Condition'):
                    cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        former_rule = epoch_logs[j]
                        frm_rule_id = former_rule["id"]
                        if [cond_dev, cond_state] in former_rule["Action"]:
                            pair_cp = (frm_rule_id, cur_rule_id)
                            conflict_device = cond_dev  # **冲突设备**
                            if pair_cp not in logged_pairs:
                                logged_pairs.add(pair_cp)
                                rc_dict["CP"].append(pair_cp)
                                rc_dict_with_device["CP"].append((pair_cp, conflict_device))
                            break

    return rc_dict, rc_dict_with_device  # **返回冲突对和对应的冲突设备**


def read_static_logs(log_file):
    """
    读取 `static_logs.txt`，解析成按轮次 (epoch) 分组的日志。
    """
    with open(log_file, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # **按照空行分隔轮次**
    epochs = data.split("\n\n")

    logs_per_epoch = []
    for epoch in epochs:
        log_entries = [ast.literal_eval(line) for line in epoch.split("\n") if line.strip()]
        logs_per_epoch.append(log_entries)

    return logs_per_epoch  # **返回按轮次分组的日志**


def sort_by_score(logs_per_epoch, rc_dict, rc_dict_with_device):
    """
    重新排序 Race Condition 结果，使得 `score` 更大的规则在左边，仅在同一轮次内调整。
    同时，对 `rc_dict_with_device` 进行同步排序，保持设备信息正确。
    """

    # **构建轮次内的 `score_map`**
    epoch_score_maps = []
    for epoch_logs in logs_per_epoch:
        score_map = {rule["id"]: rule["score"] for rule in epoch_logs}
        epoch_score_maps.append(score_map)

    # **调整 rc_dict 和 rc_dict_with_device**
    for conflict_type in rc_dict:
        new_pairs = []
        new_pairs_with_device = []
        for idx, (id1, id2) in enumerate(rc_dict[conflict_type]):
            # **找到 id1 和 id2 分别属于哪个轮次**
            epoch_index_1 = next((i for i, epoch in enumerate(logs_per_epoch) if id1 in [rule["id"] for rule in epoch]), None)
            epoch_index_2 = next((i for i, epoch in enumerate(logs_per_epoch) if id2 in [rule["id"] for rule in epoch]), None)

            # **如果两个 ID 在同一轮次，按 `score` 排序**
            if epoch_index_1 is not None and epoch_index_2 is not None and epoch_index_1 == epoch_index_2:
                score_map = epoch_score_maps[epoch_index_1]  # 获取该轮次的 `score_map`
                if score_map[id1] >= score_map[id2]:
                    new_pairs.append((id1, id2))
                    new_pairs_with_device.append((rc_dict_with_device[conflict_type][idx][0], rc_dict_with_device[conflict_type][idx][1]))
                else:
                    new_pairs.append((id2, id1))
                    new_pairs_with_device.append(((id2, id1), rc_dict_with_device[conflict_type][idx][1]))
            else:
                # **不同轮次，保持原顺序**
                new_pairs.append((id1, id2))
                new_pairs_with_device.append(rc_dict_with_device[conflict_type][idx])

        # **更新 rc_dict 和 rc_dict_with_device**
        rc_dict[conflict_type] = new_pairs
        rc_dict_with_device[conflict_type] = new_pairs_with_device

    return rc_dict, rc_dict_with_device  # **返回两个已排序的字典**


def get_user_scenario(log_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt"):
    """
    读取 `static_logs.txt` 并检测 Race Condition，仅在同一轮次内按照 `score` 进行排序。
    """
    logs_per_epoch = read_static_logs(log_file)  # **获取按轮次分组的日志**
    results, results_with_device = detectRaceCondition_per_epoch(logs_per_epoch)

    sorted_rc_dict, sorted_rc_dict_with_device = sort_by_score(logs_per_epoch, results, results_with_device)

    # 基于score得到满足用户定义的合理race condition执行顺序
    return sorted_rc_dict, sorted_rc_dict_with_device


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

if __name__ == "__main__":
    sorted_results, sorted_results_with_device = get_user_scenario()

    print("=== Final User Scenarios ===")
    print(f"Action Conflict (AC): {len(sorted_results['AC'])} conflicts")
    print(f"Unexpected Conflict (UC): {len(sorted_results['UC'])} conflicts")
    print(f"Condition Block (CBK): {len(sorted_results['CBK'])} conflicts")
    print(f"Condition Pass (CP): {len(sorted_results['CP'])} conflicts")

    print("\nScenario Pairs:")
    for conflict_type, pairs in sorted_results.items():
        print(f"{conflict_type} ({len(pairs)} conflicts): {pairs}")

    print(build_dependency_map(sorted_results_with_device))
