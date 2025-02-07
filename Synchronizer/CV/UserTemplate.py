import ast

def detectRaceCondition(logs):
    """
    仅统计/记录 4 类冲突：
      - Action Conflict (AC)
      - Unexpected Conflict (UC)
      - Condition Block (CBK)
      - Condition Pass (CP)

    并且避免重复日志：如果同一对 (former_rule.id, latter_rule.id, conflict_type)
    已记录过，就不再重复输出或计数。
    """

    rc_dict = {
        "AC": [],  # Action Conflict
        "UC": [],  # Unexpected Conflict
        "CBK": [],  # Condition Block
        "CP": []   # Condition Pass
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
                            if former_rule["ancestor"] == current_rule["ancestor"]:
                                pair_ac = (frm_rule_id, cur_rule_id)
                                if pair_ac not in logged_pairs:
                                    logged_pairs.add(pair_ac)
                                    rc_dict["AC"].append(pair_ac)
                            else:
                                pair_uc = (frm_rule_id, cur_rule_id)
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

def getUserTemplate(log_file=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt"):
    """
    读取 `static_logs.txt` 并检测 Race Condition。
    """
    logs = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                log_entry = ast.literal_eval(line)
                logs.append(log_entry)

    results = detectRaceCondition(logs)

    return results  # 返回标准检测结果

# 允许直接运行此文件以查看结果
if __name__ == "__main__":
    results = getUserTemplate()

    print("=== Final Detection Results ===")
    print(f"Action Conflict (AC): {len(results['AC'])} conflicts")
    print(f"Unexpected Conflict (UC): {len(results['UC'])} conflicts")
    print(f"Condition Block (CBK): {len(results['CBK'])} conflicts")
    print(f"Condition Pass (CP): {len(results['CP'])} conflicts")

    print("\nConflict Pairs:")
    for conflict_type, pairs in results.items():
        print(f"{conflict_type}: {pairs}")
