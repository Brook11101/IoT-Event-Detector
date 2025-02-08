import ast


def detectRaceCondition(logs):
    """
    仅统计/记录 4 类冲突：
      - Action Conflict (AC)
      - Unexpected Conflict (UC)
      - Condition Block (CBK)
      - Condition Pass (CP)

    先检测 Race Condition，不做排序。
    """

    rc_dict = {
        "AC": [],  # Action Conflict
        "UC": [],  # Unexpected Conflict
        "CBK": [],  # Condition Block
        "CP": []  # Condition Pass
    }

    logged_pairs = set()  # 记录 (former_rule.id, latter_rule.id, conflict_type)

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
                former_actions = former_rule["Action"]

                for former_act in former_actions:
                    if former_act[0] == cond_dev:
                        pair_cbk = (frm_rule_id, cur_rule_id)

                        if pair_cbk not in logged_pairs:
                            logged_pairs.add(pair_cbk)
                            rc_dict["CBK"].append(pair_cbk)
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
                former_actions = former_rule["Action"]

                for latter_act in current_actions:
                    for former_act in former_actions:
                        if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                            pair_ac = (frm_rule_id, cur_rule_id)
                            pair_uc = (frm_rule_id, cur_rule_id)

                            if former_rule["ancestor"] == current_rule["ancestor"]:
                                if pair_ac not in logged_pairs:
                                    logged_pairs.add(pair_ac)
                                    rc_dict["AC"].append(pair_ac)
                            else:
                                if pair_uc not in logged_pairs:
                                    logged_pairs.add(pair_uc)
                                    rc_dict["UC"].append(pair_uc)

            # Condition Pass (CP)
            if current_rule.get('Condition'):
                cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):
                    former_rule = logs[j]
                    frm_rule_id = former_rule["id"]
                    if [cond_dev, cond_state] in former_rule["Action"]:
                        pair_cp = (frm_rule_id, cur_rule_id)
                        if pair_cp not in logged_pairs:
                            logged_pairs.add(pair_cp)
                            rc_dict["CP"].append(pair_cp)
                        break

    return rc_dict


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


def reorder_by_score(logs_per_epoch, rc_dict):
    """
    重新排序 Race Condition 结果，使得 `score` 更大的规则在左边，仅在同一轮次内调整。
    最终返回 **完整的 rc_dict**，但同轮次的 pair 会被调整顺序。
    """

    # **构建轮次内的 `score_map`**
    epoch_score_maps = []
    for epoch_logs in logs_per_epoch:
        score_map = {rule["id"]: rule["score"] for rule in epoch_logs}
        epoch_score_maps.append(score_map)

    # **调整 rc_dict，但仍然存回原字典**
    for conflict_type, pairs in rc_dict.items():
        new_pairs = []
        for id1, id2 in pairs:
            # **找到 id1 和 id2 分别属于哪个轮次**
            epoch_index_1 = next((i for i, epoch in enumerate(logs_per_epoch) if id1 in [rule["id"] for rule in epoch]),
                                 None)
            epoch_index_2 = next((i for i, epoch in enumerate(logs_per_epoch) if id2 in [rule["id"] for rule in epoch]),
                                 None)

            # **如果两个 ID 在同一轮次，按 `score` 排序**
            if epoch_index_1 is not None and epoch_index_2 is not None and epoch_index_1 == epoch_index_2:
                score_map = epoch_score_maps[epoch_index_1]  # 获取该轮次的 `score_map`
                if score_map[id1] >= score_map[id2]:
                    new_pairs.append((id1, id2))
                else:
                    new_pairs.append((id2, id1))
            else:
                # **不同轮次，保持原顺序**
                new_pairs.append((id1, id2))

        # **更新 rc_dict**
        rc_dict[conflict_type] = new_pairs

    return rc_dict  # **返回已调整的完整 rc_dict**


def getUserTemplate(log_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt"):
    """
    读取 `static_logs.txt` 并检测 Race Condition，仅在同一轮次内按照 `score` 进行排序。
    """
    logs_per_epoch = read_static_logs(log_file)  # **获取按轮次分组的日志**

    # **展开日志**
    logs = [rule for epoch in logs_per_epoch for rule in epoch]

    results = detectRaceCondition(logs)  # **先检测 Race Condition**
    sorted_rc_dict = reorder_by_score(logs_per_epoch, results)  # **在同一轮次内排序**

    return sorted_rc_dict  # **返回最终结果**


if __name__ == "__main__":
    sorted_results = getUserTemplate()

    print("=== Final Detection Results (Reordered) ===")
    print(f"Action Conflict (AC): {len(sorted_results['AC'])} conflicts")
    print(f"Unexpected Conflict (UC): {len(sorted_results['UC'])} conflicts")
    print(f"Condition Block (CBK): {len(sorted_results['CBK'])} conflicts")
    print(f"Condition Pass (CP): {len(sorted_results['CP'])} conflicts")

    print("\nConflict Pairs:")
    for conflict_type, pairs in sorted_results.items():
        print(f"{conflict_type} ({len(pairs)} conflicts): {pairs}")
