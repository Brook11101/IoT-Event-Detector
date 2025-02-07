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

    conflict_dict = {
        "AC": [],  # Action Conflict
        "UC": [],  # Unexpected Conflict
        "CBK": [],  # Condition Block
        "CP": []   # Condition Pass
    }

    action_conflict_count = 0      # AC
    unexpected_conflict_count = 0  # UC
    condition_block_count = 0      # CBK
    condition_pass_count = 0       # CP

    logged_pairs = set()  # 记录 (former_rule.id, latter_rule.id, conflict_type)

    with open("race_condition.txt", "a", encoding="utf-8") as rc_file:
        for i in range(len(logs)):
            current_rule = logs[i]
            current_actions = current_rule["Action"]
            cur_rule_id = current_rule["id"]

            # ========== 1) Condition Block (CBK) ========== #
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
                                condition_block_count += 1
                                conflict_dict["CBK"].append(pair_cbk)

                                rc_file.write("Condition Block\n")
                                rc_file.write(str(former_rule) + "\n")
                                rc_file.write(str(current_rule) + "\n\n")
                            break
                    else:
                        continue
                    break

            # ========== 2) 其他三个冲突只在 'run' 规则里检测 ========== #
            if current_rule['status'] == 'run':
                # ---- (A) Action Conflict / Unexpected Conflict ----
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
                                        action_conflict_count += 1
                                        conflict_dict["AC"].append(pair_ac)

                                        rc_file.write("Action Conflict\n")
                                        rc_file.write(str(former_rule) + "\n")
                                        rc_file.write(str(current_rule) + "\n\n")
                                else:
                                    pair_uc = (frm_rule_id, cur_rule_id)
                                    if pair_uc not in logged_pairs:
                                        logged_pairs.add(pair_uc)
                                        unexpected_conflict_count += 1
                                        conflict_dict["UC"].append(pair_uc)

                                        rc_file.write("Unexpected Conflict\n")
                                        rc_file.write(str(former_rule) + "\n")
                                        rc_file.write(str(current_rule) + "\n\n")

                # ---- (B) Condition Pass (CP) ----
                if current_rule.get('Condition'):
                    cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        former_rule = logs[j]
                        frm_rule_id = former_rule["id"]
                        if [cond_dev, cond_state] in former_rule["Action"]:
                            pair_cp = (frm_rule_id, cur_rule_id)
                            if pair_cp not in logged_pairs:
                                logged_pairs.add(pair_cp)
                                condition_pass_count += 1
                                conflict_dict["CP"].append(pair_cp)

                                rc_file.write("Condition Pass\n")
                                rc_file.write(str(former_rule) + "\n")
                                rc_file.write(str(current_rule) + "\n\n")
                            break

    return conflict_dict



if __name__ == "__main__":
    import ast


    # 读取execution_logs.txt
    logs = []
    with open("execution_logs.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                # 用ast.literal_eval将字符串(形如"{'key': value, ...}")解析成dict
                log_entry = ast.literal_eval(line)
                logs.append(log_entry)

        # 初始化日志文件（清空）
        with open("race_condition.txt", "w", encoding="utf-8"):
            pass

    # 调用检测函数
    conflict_results = detectRaceCondition(logs)

    # 控制台打印结果，便于查看
    print("=== Final Detection Results ===")
    print(f"Action Conflict (AC): {len(conflict_results['AC'])} conflicts")
    print(f"Unexpected Conflict (UC): {len(conflict_results['UC'])} conflicts")
    print(f"Condition Block (CBK): {len(conflict_results['CBK'])} conflicts")
    print(f"Condition Pass (CP): {len(conflict_results['CP'])} conflicts")

    # 详细输出
    print("\nConflict Pairs:")
    for conflict_type, pairs in conflict_results.items():
        print(f"{conflict_type}: {pairs}")